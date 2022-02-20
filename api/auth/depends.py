from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidAudienceError

from .utils.request import get_server_secret
from .models.token import Token


def get_token(request: Request) -> str:
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        if auth_header is not None and auth_header.startswith('Bearer '):
            return auth_header[len('Bearer '):]
    return None


class CheckScope:
    def __init__(self, scope: str = None):
        self.scope = scope

    async def __call__(
        self,
        request: Request,
        bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        server_secret: str = Depends(get_server_secret)
    ) -> str:
        if bearer_token:
            token = bearer_token.credentials
            return self.get_token(request, token, server_secret)
        else:
            raise HTTPException(
                status_code=403, detail='Authentication required')

    def get_token(self, request: Request, token: str, server_secret: str):
        decoded_token = self.get_decoded_token(token, server_secret)
        if decoded_token:
            request.state.scopes = decoded_token.aud
            request.state.username = decoded_token.sub
            return decoded_token.sub
        raise HTTPException(status_code=403, detail='Authentication required')

    def get_decoded_token(self, token: str, server_secret: str) -> Token:
        if token and server_secret:
            try:
                decoded_token = Token.from_string(
                    token, server_secret, self.scope)
                if decoded_token:
                    return decoded_token
            except ExpiredSignatureError:
                raise HTTPException(status_code=401, detail='Token expired')
            except InvalidAudienceError:
                raise HTTPException(
                    status_code=403,
                    detail='User doesn\'t have the appropriate roles assigned'
                )
        return None


async def get_scopes(request: Request):
    try:
        return request.state.scopes
    except AttributeError:
        return None


async def get_username(request: Request):
    try:
        return request.state.username
    except AttributeError:
        return None
