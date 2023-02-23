from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Type
from datetime import datetime, timedelta, timezone
from calendar import timegm
from uuid import uuid4
from jwt import encode, decode
from jwt.exceptions import (
    DecodeError, InvalidKeyError, ImmatureSignatureError,
    InvalidAlgorithmError, PyJWKError, PyJWKSetError, PyJWKClientError
)
from traceback import print_exc
from sys import stderr

from ..models.user_information import UserInformation


def now() -> datetime:
    return datetime.now(tz=timezone.utc)


def now_tuple():
    return now().utctimetuple()


def now_plus_minutes(minutes: int) -> tuple:
    return (now() + timedelta(minutes=minutes)).utctimetuple()


def tgm(t: tuple = now_tuple()) -> int:
    return timegm(t)


class Token(BaseModel):
    iss: str = ''
    sub: str = ''
    aud: str = ''
    exp: int = Field(default_factory=lambda: tgm(now_plus_minutes(60)))
    nbf: int = Field(default_factory=lambda: tgm())
    iat: int = Field(default_factory=lambda: tgm())
    jti: str = Field(default_factory=lambda: str(uuid4()))
    username: str = ''
    user_id: str = ''
    display_name: str = ''
    email: str = ''
    scopes: List[str] = []

    @ classmethod
    def from_string(cls: Type['Token'], token: str, key: str, hostname: str) -> Optional['Token']:  # noqa: E501
        decoded_token = cls.decode_token_string(token, key, hostname)
        if decoded_token:
            return Token(**decoded_token)
        return None

    @ staticmethod
    def decode_token_string(token: str, key: str, hostname: str) -> Optional[Dict[str, Any]]:  # noqa: E501
        try:
            return decode(
                token,
                verify=True,
                key=key,
                algorithms=['HS512'],
                audience=hostname,
            )
        except (
            DecodeError,
            InvalidKeyError,
            ImmatureSignatureError,
            InvalidAlgorithmError,
            PyJWKError,
            PyJWKSetError,
            PyJWKClientError
        ):
            print_exc(file=stderr)
            return None

    def to_string(self, key: str) -> str:
        token_dict = self.dict()
        return encode(token_dict, key, algorithm='HS512')


class TokenResponse(BaseModel):
    token: str = ''
    token_type: str = ''

    @classmethod
    def create_token(
        cls,
        hostname: str,
        user_information: UserInformation,
        username: str,
        scopes: List[str],
        server_secret: str,
        jti: str,
    ) -> 'TokenResponse':
        token = Token(
            iss=hostname,
            sub=user_information.username,
            aud=hostname,
            jti=jti,
            username=username,
            display_name=user_information.display_name,
            email=user_information.email,
            scopes=scopes
        )
        encoded_token = token.to_string(server_secret)
        return cls(token=encoded_token, token_type='bearer')
