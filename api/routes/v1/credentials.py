from logging import error, exception, info
from traceback import print_exc
from odmantic import AIOEngine
from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from datetime import datetime
from redis import Redis
from amqpstorm.management import ManagementApi

from .models.credentials import (
    ManagementCredentials,
    ManagementCredentialsCollection,
    ManagementCredentialsResponse
)
from .models.namespace import Namespace
from .settings import default_mongodb_host
from .settings import default_mongodb_port
from .settings import default_mongodb_extra_args
from .settings import default_rabbitmq_host
from .settings import default_rabbitmq_port
from .settings import default_redis_host
from .settings import default_redis_port

from .utils import (
    check_namespace_allowed, decrypt, get_allowed_namespace,
    get_odm_session, get_rabbitmq_management_api, get_redis_client
)

from ...auth.depends import CheckScope, get_username


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.post(
    "/{namespace}/credentials",
    summary="Create credentials for a namespace",
    response_model=Union[str, dict],  # type: ignore
    dependencies=[user_role]
)
async def create_credentials(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    redis_client: Redis = Depends(get_redis_client),
    rabbitmq_management_api: ManagementApi = Depends(get_rabbitmq_management_api),  # noqa: E501
    namespace_obj: Namespace = Depends(get_allowed_namespace)
) -> Union[str, dict]:
    """Create credentials for a namespace.
    Encrypt the credentials and
    return the password to retrieve the credentials.
    Return an error if the namespace does not exist

    Raises:
        HTTPException: Raises exception if credentials could not be created
        HTTPException: Raises exception if namespace does not exist or user
            has no access

    Returns:
        ManagementCredentials(Object)
    """
    if namespace_obj:
        info(f"namespace {namespace} found")
        credentials = await ManagementCredentials.get(database, namespace)
        if credentials:
            # delete existing credentials
            await ManagementCredentials.delete_one(database, namespace, namespace_obj.domain)  # noqa: E501
            info(f"existing credentials for {namespace} deleted")
        else:
            info(f"credentials for namespace {namespace} not found")
        domain = namespace_obj.domain
        password = await ManagementCredentials.new(
            database, rabbitmq_management_api, redis_client,
            namespace, domain, username,
            default_mongodb_host, default_mongodb_port, default_mongodb_extra_args,  # noqa: E501
            default_rabbitmq_host, default_rabbitmq_port,
            default_redis_host, default_redis_port,
        )
        if password:
            namespace_obj.updated_at = datetime.utcnow()
            namespace_updated = await database.save(namespace_obj)
            if namespace_updated and namespace_updated.id:
                info(f"namespace {namespace} updated")
                return password
            else:
                error(f"namespace {namespace} update failed")
        else:
            error(f"credentials for namespace {namespace} not created")
        raise HTTPException(status_code=500, detail="Could not create credentials")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.get(
    '/{namespace}/credentials',
    response_model=ManagementCredentialsResponse,
    dependencies=[user_role, Depends(check_namespace_allowed)]
)
async def get_credentials(
    namespace: str,
    key: str,
    database: AIOEngine = Depends(get_odm_session)
) -> ManagementCredentials:
    """
    Get credentials for the current user.
    1. check, if the current user has access to the requested namespace
    2. check, if the credentials are already stored in the database
    3. if not, create new credentials and store them in the database
    4. the credentials are only valid a limited amount of time
    5. return the credentials
    """
    info("namespace found")
    credentials: Union[ManagementCredentials, None] = await ManagementCredentials.get(database, namespace)  # noqa: E501
    if credentials:  # noqa: E501
        info("credentials found")
        # decrypt the credentials
        try:
            info(f"key: {key}")
            decryption_result: bytes = b''
            if isinstance(credentials.credentials, str):
                decryption_result = decrypt(credentials.credentials, key)
            credentials_data: str = decryption_result.decode('utf-8')  # noqa: E501
            credentials_data_obj = ManagementCredentialsCollection.parse_raw(credentials_data)  # noqa: E501
            credentials.credentials = credentials_data_obj
            return credentials
        except Exception as e:
            exception(e)
            print_exc()
            raise HTTPException(status_code=500, detail="Could not decrypt credentials")  # noqa: E501
    raise HTTPException(status_code=404, detail="Credentials not found")
