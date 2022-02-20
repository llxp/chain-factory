from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine

from .login import get_user_information

from .utils.request import get_odm_session, get_idp_credentials
from .depends import CheckScope
from .models.idp_domain_config import IdpDomainConfig
from .models.idp_role_config import IdpRoleConfig
from .models.credentials import Credentials
from .models.user_information import UserInformation


api = APIRouter()


async def get_scopes_by_config(
    database: AIOEngine,
    idp_config: IdpDomainConfig,
    user_information: UserInformation
):
    roles = await IdpRoleConfig.by_user(
        database, user_information, idp_config.domain)
    scopes_lists = [role.scopes for role in roles]
    scopes_list_flat = [scope for scopes in scopes_lists for scope in scopes]
    return set(scopes_list_flat)


async def get_user_information_by_config(
    database: AIOEngine,
    idp_credentials: Credentials,
    idp_config: IdpDomainConfig
):
    user_information = await get_user_information(idp_credentials, idp_config)
    if user_information:
        return dict(
            username=user_information.username,
            user_id=user_information.user_id,
            display_name=user_information.display_name,
            email=user_information.email,
            scopes=await get_scopes_by_config(
                database, idp_config, user_information)
        )
    return None


@api.get('/user_profile', dependencies=[Depends(CheckScope('user'))])
async def user_profile(
    database: AIOEngine = Depends(get_odm_session),
    idp_credentials: Credentials = Depends(get_idp_credentials)
):
    username = idp_credentials.username
    idp_config_cursor = await IdpDomainConfig.get(
        database, username)
    if idp_config_cursor:
        async for idp_config in idp_config_cursor:
            response = await get_user_information_by_config(
                database, idp_credentials, idp_config)
            if response:
                return response
    raise HTTPException(
        status_code=503, detail='user_information could not be obtained')
