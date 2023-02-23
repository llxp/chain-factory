from odmantic import AIOEngine, Model, Field, EmbeddedModel
from odmantic.engine import AIOCursor
from datetime import datetime
from typing import List, Generator, Optional, Type

from .user_information import UserInformation

from .enums import AuthType, Roles


class AuthConfig(EmbeddedModel):
    name: str
    auth_type: AuthType = Field(AuthType.GROUP, alias='auth_type')


class IdpRoleConfig(Model):
    enabled: bool = Field(default=True)
    created: datetime = Field(default=datetime.utcnow())
    updated: datetime = Field(default=datetime.utcnow())
    auth_config: List[AuthConfig]
    role: str = Roles.Default.value
    domain: str
    scopes: List[str] = []

    def allowed_scopes(
        self,
        scopes: List[str]
    ) -> Generator[str, None, None]:
        for scope in self.scopes:
            if scope in scopes:
                yield scope
        return None

    @classmethod
    async def by_user(
        cls: Type['IdpRoleConfig'],
        database: AIOEngine,
        user_information: UserInformation,
        domain: str = 'default'
    ) -> List['IdpRoleConfig']:
        groups = user_information.groups
        username = user_information.username
        return await cls.by_user_groups(database, username, groups, domain)

    @classmethod
    async def by_user_groups(
        cls: Type['IdpRoleConfig'],
        database: AIOEngine,
        user: str,
        groups: List[str],
        domain: str
    ) -> List['IdpRoleConfig']:
        role_configs = await cls.get(database, domain)
        roles: List[IdpRoleConfig] = []
        if user and groups and role_configs:
            role_config: Optional[IdpRoleConfig] = None
            async for role_config in role_configs:
                for auth_config in role_config.auth_config:
                    if await cls.check_auth_config(auth_config, groups, user):
                        roles.append(role_config)
        return roles

    @classmethod
    async def check_auth_config(
        cls: type,
        auth_config: AuthConfig,
        groups: List[str],
        user: str
    ):
        if str(auth_config.auth_type) == str(AuthType.GROUP):
            if auth_config.name in groups:
                return True
        elif auth_config.auth_type == AuthType.USER:
            if auth_config.name == user:
                return True
        return False

    @classmethod
    async def get(
        cls: Type['IdpRoleConfig'],
        database: AIOEngine,
        domain: str
    ) -> Optional[AIOCursor['IdpRoleConfig']]:
        if domain:
            return database.find(
                cls,
                cls.domain == domain, cls.enabled == True  # noqa
            )
        return None
