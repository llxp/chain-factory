from calendar import timegm
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError, loads
from uuid import uuid4
from fastapi import HTTPException
from pydantic import BaseModel, Field
from jose.jwe import decrypt
from jose.exceptions import JOSEError, JWKError, JWEError


class CredentialsToken(BaseModel):
    username: str = ''
    password: str = ''
    exp: int = Field(default=timegm(
        (datetime.now(tz=timezone.utc) + timedelta(hours=24)).utctimetuple()
    ))
    nbf: int = Field(default=timegm(
        datetime.now(tz=timezone.utc).utctimetuple()))
    iat: int = Field(default=timegm(
        datetime.now(tz=timezone.utc).utctimetuple()))
    jti: str = Field(default=str(uuid4()))

    @classmethod
    def from_string(
        cls: type['CredentialsToken'],
        token: str,
        key: str
    ) -> 'CredentialsToken':
        if token:
            decrypted_token: bytes = cls.decrypt_token(token, key)
            if decrypted_token:
                token_str: str = cls.decode_bytes_token(decrypted_token)
                return cls.from_json(token_str)
        return None

    @classmethod
    def from_string_and_check(
        cls: type['CredentialsToken'],
        token: str,
        key: str
    ) -> 'CredentialsToken':
        token: cls = cls.from_string(token, key)
        if not token:
            raise HTTPException(
                status_code=401, detail='Invalid refresh token')
        return token if token.check_token() else None

    @classmethod
    def decrypt_token(cls: type, token: str, key: str) -> bytes:
        try:
            return decrypt(token, key)
        except (JOSEError, JWKError, JWEError):
            return None

    @classmethod
    def decode_bytes_token(cls: type, bytes_token: bytes) -> str:
        return bytes_token.decode('utf-8')

    @classmethod
    def from_json(cls: type, json_str: str) -> 'CredentialsToken':
        try:
            token_dict = loads(json_str)
            return CredentialsToken(**token_dict)
        except (JSONDecodeError, TypeError):
            return None

    def check_token(self):
        now = timegm(datetime.utcnow().utctimetuple())
        expired_gt_nbf = self.exp > self.nbf
        expired_lt_now = self.exp < now
        nbf_lt_exp = self.nbf < self.exp
        nbf_lt_now = self.nbf < now
        return (
            expired_gt_nbf and
            not expired_lt_now and
            nbf_lt_exp and
            nbf_lt_now
        )
