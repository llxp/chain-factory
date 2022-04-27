from logging import error, info
from odmantic import AIOEngine
from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from aioredis import Redis
from amqpstorm.management import ManagementApi

from .models.credentials import (
    ManagementCredentials,
    ManagementCredentialsCollection,
    ManagementCredentialsResponse
)
from .settings import (
    default_mongodb_host, default_mongodb_port,
    default_rabbitmq_host, default_rabbitmq_port,
    default_redis_host, default_redis_port
)

from ...auth.utils.credentials import get_domain

from .utils import (
    decrypt, get_odm_session, get_rabbitmq_management_api, get_redis_client
)

from .models.namespace import Namespace
from ...auth.depends import CheckScope, get_username


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.post(
    "/credentials",
    summary="Create credentials for a namespace",
    response_model=Union[str, dict],
    dependencies=[user_role]
)
async def create_credentials(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    redis_client: Redis = Depends(get_redis_client),
    rabbitmq_management_api: ManagementApi = Depends(
        get_rabbitmq_management_api)
) -> Union[str, dict]:
    """Create credentials for a namespace.
    Encrypt the credentials and
    return the password to retrieve the credentials.
    Return an error if the namespace does not exist
    """
    if await Namespace.is_allowed(namespace, database, username):
        domain = await get_domain(username)
        info("namespace found")
        credentials = await ManagementCredentials.get(
            database, namespace, domain)
        if credentials:
            # delete existing credentials
            await ManagementCredentials.delete_one(
                database, namespace, domain)
        error("credentials not found")
        password = await ManagementCredentials.new(
            database,
            rabbitmq_management_api,
            redis_client,
            namespace,
            domain,
            username,
            default_mongodb_host,
            default_mongodb_port,
            default_rabbitmq_host,
            default_rabbitmq_port,
            default_redis_host,
            default_redis_port,
        )
        if password:
            return password
        raise HTTPException(
            status_code=500,
            detail="Could not create credentials"
        )
    raise HTTPException(
        status_code=404,
        detail="Namespace not found or not allowed"
    )


@ api.get(
    '/credentials',
    response_model=ManagementCredentialsResponse,
    dependencies=[user_role]
)
async def get_credentials(
    namespace: str,
    key: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username)
) -> Union[str, dict]:
    """
    Get credentials for the current user.
    1. check, if the current user has access to the requested namespace
    2. check, if the credentials are already stored in the database
    3. if not, create new credentials and store them in the database
    4. the credentials are only valid a limited amount of time
    5. return the credentials
    """
    if await Namespace.is_allowed(namespace, database, username):
        domain = await get_domain(username)
        info("namespace found")
        credentials: ManagementCredentials = await ManagementCredentials.get(
            database, namespace, domain)
        if credentials:
            info("credentials found")
            # decrypt the credentials
            try:
                credentials_data: str = decrypt(credentials.credentials, key)
                credentials_data = ManagementCredentialsCollection.parse_raw(
                    credentials_data)
                credentials.credentials = credentials_data
                return credentials
            except Exception as e:
                error(e)
                raise HTTPException(
                    status_code=500, detail="Could not decrypt credentials")
        raise HTTPException(status_code=404, detail="Credentials not found")
    raise HTTPException(
        status_code=404, detail="Namespace not found or not allowed")
