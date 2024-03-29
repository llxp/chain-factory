from distutils.log import debug
from odmantic import AIOEngine, Model, Field, EmbeddedModel
from odmantic.engine import AIOCursor
from datetime import datetime
from typing import Optional, Union

from ..utils.credentials import get_domain


class IdpEndpointConfig(EmbeddedModel):
    user_information_endpoint: Optional[str] = Field(default='')
    translate_users_endpoint: Optional[str] = Field(default='')


class IdpClientCertConfig(EmbeddedModel):
    cert: str
    key: str


class IdpDomainConfig(Model):
    enabled: bool = Field(default=True)
    created: datetime = Field(default=datetime.utcnow())
    updated: datetime = Field(default=datetime.utcnow())
    domain: str
    endpoints: IdpEndpointConfig = Field(default=None)
    client_cert_config: IdpClientCertConfig = Field(default=None)

    @classmethod
    async def get(
        cls: type,
        database: AIOEngine,
        username: str
    ) -> Union[AIOCursor['IdpDomainConfig'], None]:
        debug(f"get idp domain config for user {username}")
        domain = await get_domain(username)
        if domain:
            debug(f"domain: {domain}")
            return database.find(IdpDomainConfig, (
                (IdpDomainConfig.domain == domain) &
                (IdpDomainConfig.enabled == True)  # noqa: E712
            ))
        return None
