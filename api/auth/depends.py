from typing import Optional
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBase, HTTPBearerModel, get_authorization_scheme_param  # noqa: E501
from starlette.status import HTTP_403_FORBIDDEN
from jwt import ExpiredSignatureError, InvalidAudienceError

from .utils.request import get_server_secret
from .models.token import Token


def get_token(request: Request) -> str:
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        if auth_header is not None and auth_header.startswith('Bearer '):
            return auth_header[len('Bearer '):]
    return None


class HTTPBearer(HTTPBase):
    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)  # noqa: E501
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            print(request.cookies)
            cookie = request.cookies.get("Authorization")
            if (cookie is not None) and cookie.startswith("Bearer "):
                authorization = cookie
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")  # noqa: E501
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)  # noqa: E501


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
        raise HTTPException(status_code=403, detail='Authentication required')

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
                raise HTTPException(status_code=403, detail='Token expired')
            except InvalidAudienceError:
                raise HTTPException(
                    status_code=401,
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
