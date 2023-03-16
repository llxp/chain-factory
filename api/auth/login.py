# from json import dumps
from logging import error, info, debug, warning
from os import getenv
from uuid import uuid4
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from httpx import ConnectError, ConnectTimeout
from odmantic import AIOEngine
from httpx import AsyncClient
from typing import List, Union
from jose.jwe import encrypt
from pydantic import ValidationError
from ssl import SSLCertVerificationError

from .models.idp_domain_config import IdpDomainConfig
from .models.refresh_token import RefreshToken

from .models.idp_role_config import IdpRoleConfig
from .models.credentials import Credentials
from .models.login_request import LoginRequest
from .models.user_information import UserInformation
from .models.token import TokenResponse
from .models.credentials_token import CredentialsToken
from .utils.credentials import get_domain
from .utils.https import get_verify_context
from .utils.request import get_server_secret, get_odm_session


breakglass_username = getenv("BREAKGLASS_USERNAME", "breakglass")
breakglass_domain = getenv("BREAKGLASS_DOMAIN", "breakglass")
breakglass_password = getenv("BREAKGLASS_PASSWORD", "breakglass")


api = APIRouter()


@api.post('/login')
async def login(
    request: Request,
    response: Response,
    credentials: LoginRequest,
    database: AIOEngine = Depends(get_odm_session),
    server_secret: str = Depends(get_server_secret)
):
    # breakglass section
    # --------------------------------
    breakglass_user = f"{breakglass_username}@{breakglass_domain}"
    if credentials.username == breakglass_user and credentials.password == breakglass_password:  # noqa: E501
        warning(f"breakglass login for user {breakglass_username}")
        hostname = request.url.hostname or ""
        user_information = UserInformation(
            user_id=breakglass_username,
            username=breakglass_username,
            display_name=breakglass_username,
            email=breakglass_username,
            groups=['breakglass'],
        )
        return await create_tokens(hostname, credentials, server_secret, user_information, database, response)  # noqa: E501
    # --------------------------------
    if credentials.username and credentials.password:
        debug(f"login request: {credentials.username}")
        idp_configs = await IdpDomainConfig.get(database, credentials.username)
        # check for every host if the credentials are valid
        # and then get the user information
        if idp_configs:
            debug(f"idp config found: {len(await idp_configs)}")
            config: Union[IdpDomainConfig, None] = None
            async for config in idp_configs:
                debug(f"idp config found: {config.domain}")
                user_information = await get_user_information(credentials, config)  # noqa: E501
                if user_information:
                    hostname = request.url.hostname or ""
                    info(user_information)
                    return await create_tokens(hostname, credentials, server_secret, user_information, database, response)  # noqa: E501
    info(f"login failed for user {credentials.username}")
    raise HTTPException(status_code=403, detail='authentication failed')


async def create_tokens(hostname: str, credentials: LoginRequest, server_secret: str, user_information: UserInformation, database: AIOEngine, response: Response):  # noqa: E501
    """Creates access & refresh token,
    set them as cookies and return them additionally

    Args:
        hostname (str): Rest API Hostname
        credentials (LoginRequest): Login POST body
            (username, password, scopes)
        server_secret (str): Server secret used for jwt signage and
            jwe encryption
        user_information (UserInformation): Result from authentication
            API request
        database (AIOEngine): Database session (odmantic)
        response (Response): FastAPI Response object

    Returns:
        Dict: Access token, Refresh token
    """
    jti = str(uuid4())
    access_token = await create_token(
        hostname,
        credentials,
        server_secret,
        user_information,
        credentials.username,
        database,
        jti,
    )
    refresh_token = TokenResponse(
        token=await create_refresh_token(
            database,
            hostname,
            server_secret,
            user_information,
            credentials,
            jti
        ),
        token_type='bearer'
    )
    response.delete_cookie(key='Authorization')
    response.set_cookie(
        key='Authorization',
        value='Bearer ' + access_token.token,
        max_age=60 * 60,  # cookie will expire in 60 minutes
        httponly=True,
        samesite='none',
        secure=True,
    )
    response.delete_cookie(key='RefreshToken')
    response.set_cookie(
        key='RefreshToken',
        value='Bearer ' + refresh_token.token,
        max_age=60 * 60 * 24,  # cookie will expire in 24 hours
        httponly=True,
        samesite='none',
        secure=True,
    )
    return dict(access_token=access_token, refresh_token=refresh_token)  # noqa: E501
    # return response


async def get_user_information(
    credentials: Credentials,
    idp_config: IdpDomainConfig
) -> Union[UserInformation, None]:
    headers = {'content-type': 'application/json'}
    url = idp_config.endpoints.user_information_endpoint or ""
    cert_context = await get_verify_context(url, idp_config)
    async with AsyncClient(verify=cert_context) as client:
        try:
            response = await perform_user_information_request(credentials, headers, client, url)  # noqa: E501
            debug(f"user information request response: {response}")
            if response:
                debug(f"user information request success: {url}")
                return response
        except ConnectError:
            error(f"user information request failed with connect error: {url}")
            return None
        except ConnectTimeout:
            error(f"user information request failed with timeout: {url}")
            return None
        except SSLCertVerificationError as e:
            error(f"user information request failed with ssl error: {url}, error: {e}")  # noqa: E501
            return None
    error(f"user information request failed: {url}")
    return None


async def perform_user_information_request(
    credentials: Credentials,
    headers: dict,
    client: AsyncClient,
    url: str
) -> Union[UserInformation, None]:
    if url:
        credentials_json = credentials.json()
        user_information_response = await client.post(url=url, data=credentials_json, headers=headers, timeout=10)  # type: ignore  # noqa: E501
        if user_information_response.status_code == 200:
            response = user_information_response.json()
            try:
                return UserInformation(**response)
            except ValidationError:
                debug(f"invalid user information response: {response}")
                return None
        error(f"response was: {user_information_response.text}")
    error(f"user information request failed: {url}")
    return None


def get_scopes(
    scopes: List[str] = [],
    roles: List[IdpRoleConfig] = []
) -> Union[List[str], None]:
    if not scopes:
        return None
    allowed_scopes: List[str] = []
    for role in roles:
        allowed_scopes.extend(role.allowed_scopes(scopes))
    not_allowed_scopes = [
        scope
        for scope in scopes
        if scope not in allowed_scopes
    ]
    if len(not_allowed_scopes) > 0:
        scopes_text = f"scope{'s' if len(not_allowed_scopes) > 1 else ''}"
        scopes_str = ', '.join(not_allowed_scopes)
        raise HTTPException(
            status_code=403, detail=f"{scopes_text} {scopes_str} not allowed")
    return allowed_scopes


async def create_token(
    hostname: str,
    credentials: LoginRequest,
    server_secret: str,
    user_information: UserInformation,
    username: str,
    database: AIOEngine,
    jti: str,
):
    # user has roles
    domain = await get_domain(credentials.username)
    roles = await IdpRoleConfig.by_user(database, user_information, domain)
    # a role has a group of scopes
    # aud/audience is the list of scopes
    requested_scopes = credentials.scopes or []
    allowed_scopes = get_scopes(requested_scopes, roles) or []
    token_response = TokenResponse.create_token(hostname, user_information, username, allowed_scopes, server_secret, jti)  # noqa: E501
    if not token_response:
        raise HTTPException(status_code=400, detail='no scopes requested')  # noqa: E501
    return token_response


async def create_refresh_token(
    database,
    hostname: str,
    server_secret: str,
    user_information: UserInformation,
    credentials: LoginRequest,
    jti: str,
):
    token = CredentialsToken(
        iss=hostname,
        username=credentials.username,
        password=credentials.password,
        jti=jti,
    )
    new_refresh_token = RefreshToken(
        jti=token.jti,
        username=user_information.username,
        expires_at=token.exp,
        created_at=token.iat,
        scopes=credentials.scopes,
        user_id=user_information.user_id,
        display_name=user_information.display_name,
        email=user_information.email,
    )
    await database.save(new_refresh_token)
    encrypted_bytes = encrypt(
        plaintext=token.json(),
        key=server_secret,
        algorithm='dir',
        encryption='A256CBC-HS512',
    )
    return encrypted_bytes.decode('utf-8')
