from logging import error, info
from fastapi import APIRouter, Depends, Request, HTTPException
from httpx import ConnectError, ConnectTimeout
from odmantic import AIOEngine
from httpx import AsyncClient
from typing import List
from jose.jwe import encrypt
from pydantic import ValidationError

from .models.idp_domain_config import IdpDomainConfig
from .models.refresh_token import RefreshToken

from .models.idp_role_config import IdpRoleConfig
from .models.credentials import Credentials
from .models.login_request import LoginRequest
from .models.user_information import UserInformation
from .models.token import TokenResponse
from .models.credentials_token import CredentialsToken
from .utils.credentials import get_domain
from .utils.https import get_https_certificates
from .utils.request import get_server_secret, get_odm_session


api = APIRouter()


@api.post('/login')
async def login(
    request: Request,
    credentials: LoginRequest,
    database: AIOEngine = Depends(get_odm_session),
    server_secret: str = Depends(get_server_secret)
):
    if credentials.username and credentials.password:
        idp_config = await IdpDomainConfig.get(
            database, credentials.username)
        # check for every host if the credentials are valid
        # and then get the user information
        if idp_config:
            config: IdpDomainConfig = None
            async for config in idp_config:
                user_information = await get_user_information(
                    credentials, config)
                if user_information:
                    hostname = request.url.hostname
                    info(user_information)
                    return dict(
                        access_token=await create_token(
                            hostname,
                            credentials,
                            server_secret,
                            user_information,
                            database,
                        ),
                        refresh_token=TokenResponse(
                            token=await create_refresh_token(
                                database,
                                hostname,
                                server_secret,
                                credentials
                            ),
                            token_type='bearer'
                        )
                    )
    info(f"login failed for user {credentials.username}")
    raise HTTPException(status_code=403, detail='authentication failed')


async def get_user_information(
    credentials: Credentials,
    idp_config: IdpDomainConfig
) -> UserInformation:
    headers = {'content-type': 'application/json'}
    url = idp_config.endpoints.user_information_endpoint
    client_certificates = await get_https_certificates(url, idp_config)
    async with AsyncClient(cert=client_certificates) as client:
        try:
            response = await perform_user_information_request(
                credentials, headers, client, url)
            if response:
                return response
        except ConnectError:
            return None
        except ConnectTimeout:
            return None


async def perform_user_information_request(
    credentials: Credentials,
    headers: dict,
    client: AsyncClient,
    url: str
):
    if url:
        credentials_json = credentials.json()
        user_information_response = await client.post(
            url=url, data=credentials_json, headers=headers, timeout=10)
        if user_information_response.status_code == 200:
            response = user_information_response.json()
            try:
                return UserInformation(**response)
            except ValidationError:
                return None
    error(f"user information request failed: {url}")
    return None


def get_scopes(
    scopes: List[str] = [],
    roles: List[IdpRoleConfig] = []
) -> List[str]:
    if not scopes:
        return None
    allowed_scopes: List[str] = []
    for role in roles:
        allowed_scopes.extend(role.allowed_scopes(scopes))
    not_allowed_scopes = [
        scope for scope in scopes if scope not in allowed_scopes]
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
    database: AIOEngine,
):
    # user has roles
    domain = await get_domain(credentials.username)
    roles = await IdpRoleConfig.by_user(database, user_information, domain)
    # a role has a group of scopes
    # aud/audience is the list of scopes
    requested_scopes = credentials.scopes
    allowed_scopes = get_scopes(requested_scopes, roles)
    token_response = TokenResponse.create_token(
        hostname, credentials.username, allowed_scopes, server_secret)
    if not token_response:
        raise HTTPException(
            status_code=400, detail='no scopes requested')
    return token_response


async def create_refresh_token(
    database,
    hostname: str,
    server_secret: str,
    credentials: LoginRequest
):
    token = CredentialsToken(
        iss=hostname,
        username=credentials.username,
        password=credentials.password,
    )
    new_refresh_token = RefreshToken(
        jti=token.jti,
        username=credentials.username,
        expires_at=token.exp,
        created_at=token.iat,
        scopes=credentials.scopes
    )
    await database.save(new_refresh_token)
    return encrypt(
        plaintext=token.json(),
        key=server_secret,
        algorithm='dir',
        encryption='A256CBC-HS512',
    )
