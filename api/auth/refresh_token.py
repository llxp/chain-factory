from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from odmantic import AIOEngine

from api.auth.models.user_information import UserInformation

from .models.refresh_token import RefreshToken
from .models.token import TokenResponse
from .models.credentials_token import CredentialsToken
from .utils.request import get_hostname, get_odm_session, get_server_secret


api = APIRouter()


@api.post('/refresh_token')
async def access_token_from_refresh_token(
    bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    server_secret: str = Depends(get_server_secret),
    database: AIOEngine = Depends(get_odm_session),
    hostname: str = Depends(get_hostname),
) -> TokenResponse:
    token = await get_token(bearer_token, server_secret)
    if token:
        key = server_secret
        return await create_token(database, token, hostname, key)
    raise HTTPException(status_code=403, detail='Refresh token expired')


async def get_token(
    bearer_token: HTTPAuthorizationCredentials,
    key: str
) -> Optional[CredentialsToken]:
    token_str: str = bearer_token.credentials
    return CredentialsToken.from_string_and_check(token_str, key)


async def create_token(
    database: AIOEngine,
    token: CredentialsToken,
    hostname: str,
    key: str
) -> TokenResponse:
    db_token = await find_refresh_token(database, token.jti)
    if db_token:
        username = token.username
        scopes = db_token.scopes
        if scopes:
            user_information = UserInformation(
                username=token.username,
                user_id=db_token.user_id,
                display_name=db_token.display_name,
                email=db_token.email,
            )
            return TokenResponse.create_token(hostname, user_information, username, scopes, key, db_token.jti)  # noqa: E501
        raise HTTPException(status_code=403, detail='Scopes missing in refresh token')  # noqa: E501
    raise HTTPException(status_code=401, detail='Token is revoked')


async def find_refresh_token(database: AIOEngine, jti: str):
    return await database.find_one(
        RefreshToken,
        (
            (RefreshToken.jti == jti) &
            (RefreshToken.revoked == False)  # noqa
        )
    )
