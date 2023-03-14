from logging import debug, error
from typing import List, Optional
from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from httpx import AsyncClient, ConnectError, ConnectTimeout
from ssl import SSLCertVerificationError
from pydantic import ValidationError

from .models.translate_users_response import TranslateUsersResponse

from .models.translate_users_request import TranslateUsersRequest

from .utils.https import get_verify_context

from .models.token import Token

from .utils.request import get_idp_credentials, get_odm_session, get_token, get_username  # noqa: E501
from .depends import CheckScope
from .models.idp_domain_config import IdpDomainConfig
from .models.idp_role_config import IdpRoleConfig
from .models.credentials import Credentials
from .models.user_information import UserInformation
from .models.user_profile import UserProfile


api = APIRouter()


async def get_scopes_by_config(
    database: AIOEngine,
    idp_config: IdpDomainConfig,
    user_information: UserInformation
) -> List[str]:
    roles = await IdpRoleConfig.by_user(database, user_information, idp_config.domain)  # noqa: E501
    scopes_lists = [role.scopes for role in roles]
    scopes_list_flat = [scope for scopes in scopes_lists for scope in scopes]
    unique_scopes = set(scopes_list_flat)
    return list(unique_scopes)


async def perform_user_information_request_impersonated(
    idp_credentials: Credentials,
    user_ids: List[str],
    headers: dict,
    client: AsyncClient,
    url: str
):
    if url:
        translate_users_request = TranslateUsersRequest(
            username=idp_credentials.username,
            password=idp_credentials.password,
            user_ids=user_ids
        )
        tur_json = translate_users_request.json()
        user_information_response = await client.post(url=url, data=tur_json, headers=headers, timeout=10)  # type: ignore  # noqa: E501
        if user_information_response.status_code == 200:
            response = user_information_response.json()
            try:
                return TranslateUsersResponse(**response)
            except ValidationError:
                debug(f"invalid user information response: {response}")
                return None
        error(f"response was: {user_information_response.text}")
    error(f"user information request failed: {url}")
    return None


async def get_user_information_impersonated(
    idp_credentials: Credentials,
    idp_config: IdpDomainConfig,
    user_ids: List[str]
) -> Optional[UserInformation]:
    user_ids_lower = [user_id.lower() for user_id in user_ids]
    headers = {'content-type': 'application/json'}
    url = idp_config.endpoints.translate_users_endpoint or ""
    cert_context = await get_verify_context(url, idp_config)
    async with AsyncClient(verify=cert_context) as client:
        try:
            response = await perform_user_information_request_impersonated(idp_credentials, user_ids, headers, client, url)  # noqa: E501
            debug(f"user information request response: {response}")
            if response and response.users:
                if isinstance(response.users, dict) and len(response.users) > 0:  # noqa: E501
                    users_lower = {k.lower(): v for k, v in response.users.items()}  # noqa: E501
                    return users_lower[user_ids_lower[0]]
                elif isinstance(response.users, UserInformation):
                    return response.users
        except ConnectError:
            error(f"user information request failed with connect error: {url}")
            return None
        except ConnectTimeout:
            error(f"user information request failed with timeout: {url}")
            return None
        except SSLCertVerificationError as e:
            error(f"user information request failed with ssl error: {url}, error: {e}")  # noqa: E501
            return None


async def get_user_information_by_config(
    database: AIOEngine,
    idp_credentials: Credentials,
    idp_config: IdpDomainConfig,
    username: str
):
    user_information = await get_user_information_impersonated(idp_credentials, idp_config, [username])  # noqa: E501
    if user_information:
        return UserProfile(
            username=user_information.username,
            user_id=user_information.user_id,
            display_name=user_information.display_name,
            email=user_information.email,
            scopes=await get_scopes_by_config(database, idp_config, user_information)  # noqa: E501
        )
    return None


@api.get('/user_profile', dependencies=[Depends(CheckScope('user'))])
async def user_profile(
    token: Token = Depends(get_token),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    idp_credentials: Credentials = Depends(get_idp_credentials),
):
    idp_config_cursor = await IdpDomainConfig.get(database, username)
    if idp_config_cursor:
        async for idp_config in idp_config_cursor:
            response = await get_user_information_by_config(database, idp_credentials, idp_config, username)  # noqa: E501
            if response:
                return response
    return UserProfile(
        username=token.username,
        user_id=token.user_id,
        display_name=token.display_name,
        email=token.email,
        scopes=token.scopes
    )
