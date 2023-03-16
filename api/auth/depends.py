from logging import debug
from typing import Optional, Union
from fastapi import Depends, Request, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security.http import HTTPBase  # noqa: E501
from starlette.status import HTTP_403_FORBIDDEN
from jwt import ExpiredSignatureError, InvalidAudienceError
from odmantic import AIOEngine

from .models.user_information import UserInformation

from .utils.request import get_hostname, get_server_secret, get_odm_session
from .models.token import Token, TokenResponse
from .refresh_token import find_refresh_token, get_token as get_refresh_token


def get_token(request: Request) -> str:
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        if auth_header is not None and auth_header.startswith('Bearer '):
            return auth_header[len('Bearer '):]
    return ""


class HTTPBearer(HTTPBase):
    """Customized HTTPBearer class from FastAPI,
    adjusted to also work with cookies"""
    def __init__(
        self,
        *,
        cookie_name: str = "Authorization",
        bearer_format: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearer_format, description=description)  # type: ignore # noqa: E501
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error
        self.cookie_name = cookie_name

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        """Check if either authorization header or specified
        cookie is set and return contained token

        Args:
            request (Request): FastAPI request object

        Raises:
            HTTPException: Raise exception if no token is found in request
            HTTPException: Raise exception if token is in an invalid format

        Returns:
            Optional[HTTPAuthorizationCredentials]: Token / JWT
        """
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            # print(request.cookies)
            cookie = request.cookies.get(self.cookie_name)
            if (cookie is not None) and cookie.startswith("Bearer "):
                authorization = cookie
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")  # noqa: E501
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication credentials")  # noqa: E501
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)  # noqa: E501


class CheckScope:
    def __init__(self, scope: str = ""):
        self.scope = scope

    async def __call__(
        self,
        request: Request,
        response: Response,
        database: AIOEngine = Depends(get_odm_session),
        bearer_token: HTTPAuthorizationCredentials = Depends(HTTPBearer(cookie_name='Authorization')),  # noqa: E501
        refresh_token: HTTPAuthorizationCredentials = Depends(HTTPBearer(cookie_name='RefreshToken')),  # noqa: E501
        server_secret: str = Depends(get_server_secret),
        hostname: str = Depends(get_hostname)
    ) -> str:
        """Check authorization token for permissions.
        If not set use refresh token to generate new JWT.

        Args:
            request (Request): FastAPI request object
            response (Response): FastAPI response object
            database (AIOEngine, optional): Database object.
                Defaults to Depends(get_odm_session).
            bearer_token (HTTPAuthorizationCredentials, optional):
                Authorization token from request. Defaults to
                Depends(HTTPBearer(cookie_name='Authorization')).
            refresh_token (HTTPAuthorizationCredentials, optional):
                Refresh token from request. Defaults to
                Depends(HTTPBearer(cookie_name='RefreshToken')).
            server_secret (str, optional): Server secret to sign auth token /
                encrypt refresh token. Defaults to Depends(get_server_secret).
            hostname (str, optional): Fqdn of RestAPI. Defaults to
                Depends(get_hostname).

        Raises:
            HTTPException: Raises exception if no scopes found in refresh token
            HTTPException: Raises exception if no token is found in request

        Returns:
            str: Returns method to decode / verify access token
        """
        if bearer_token:
            token = bearer_token.credentials
            return self.get_token(request, token, server_secret, hostname)
        if refresh_token:
            token = await get_refresh_token(refresh_token, server_secret)
            if token:
                db_token = await find_refresh_token(database, token.jti)
                if db_token:
                    username = token.username
                    scopes = db_token.scopes
                    if scopes:
                        user_information = UserInformation(
                            username=db_token.username,
                            user_id=db_token.user_id,
                            display_name=db_token.display_name,
                            email=db_token.email,
                        )
                        token_response = TokenResponse.create_token(hostname, user_information, username, scopes, server_secret, db_token.jti)  # noqa: E501
                        response.set_cookie("Authorization", f"Bearer {token_response.token}", max_age=60 * 60, httponly=True, samesite='none', secure=True)  # noqa: E501
                        return self.get_token(request, token_response.token, server_secret, hostname)  # noqa: E501
                    raise HTTPException(status_code=403, detail='Scopes missing from refresh token')  # noqa: E501
        raise HTTPException(status_code=403, detail='Authentication required')

    def get_token(self, request: Request, token: str, server_secret: str, hostname: str):  # noqa: E501
        decoded_token = self.get_decoded_token(token, server_secret, hostname)
        if decoded_token:
            debug(f'Username: {decoded_token.username}')
            request.state.scopes = decoded_token.scopes
            request.state.username = decoded_token.username
            request.state.token = decoded_token
            return decoded_token.sub
        raise HTTPException(status_code=403, detail='Authentication required')

    def get_decoded_token(self, token: str, server_secret: str, hostname: str) -> Union[Token, None]:  # noqa: E501
        if token and server_secret:
            try:
                decoded_token = Token.from_string(token, server_secret, hostname)  # noqa: E501
                if decoded_token:
                    if self.scope not in decoded_token.scopes:
                        raise InvalidAudienceError('User doesn\'t have the appropriate roles assigned')  # noqa: E501
                    return decoded_token
            except ExpiredSignatureError:
                raise HTTPException(status_code=403, detail='Token expired')
            except InvalidAudienceError:
                raise HTTPException(status_code=401, detail='User doesn\'t have the appropriate roles assigned')  # noqa: E501
        return None


async def get_scopes(request: Request):
    try:
        scopes = request.state.scopes
        debug(f'Scopes: {scopes}')
        return scopes
    except AttributeError:
        return None


async def get_username(request: Request):
    try:
        username = request.state.username
        debug(f'Username: {username}')
        return username
    except AttributeError:
        return None


async def get_breakglass_username(request: Request):
    try:
        bg_username = request.state.breakglass_username
        debug(f'Breakglass Username: {bg_username}')
        return bg_username
    except AttributeError:
        return None


async def get_breakglass_domain(request: Request):
    try:
        return request.state.breakglass_domain
    except AttributeError:
        return None
