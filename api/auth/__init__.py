from fastapi import APIRouter

from .login import api as login_api
from .user_profile import api as user_profile_api
from .translate_users import api as translate_users_api
from .refresh_token import api as refresh_token_api
from .depends import CheckScope


api = APIRouter()
api.include_router(login_api, tags=['login'])
api.include_router(user_profile_api, tags=['user_profile'])
api.include_router(translate_users_api, tags=['translate_users'])
api.include_router(refresh_token_api, tags=['refresh_token'])

__all__ = [
    api,
    CheckScope,
]
