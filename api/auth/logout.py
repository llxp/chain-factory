from fastapi import APIRouter, Response, Depends
from odmantic import AIOEngine

from .depends import CheckScope

from .models.refresh_token import RefreshToken
from .models.token import Token

from .utils.request import get_odm_session, get_token


api = APIRouter()


@api.post('/logout', dependencies=[Depends(CheckScope('user'))])
async def logout(
    response: Response,
    database: AIOEngine = Depends(get_odm_session),
    token: Token = Depends(get_token),
):
    # revoke cookies
    response.delete_cookie('Authorization')
    response.delete_cookie('RefreshToken')
    # revoke tokens in database
    tokens = await database.find(RefreshToken, (RefreshToken.jti == token.jti))
    for token_obj in tokens:
        await database.delete(token_obj)
    return {'status': 'logged out'}
