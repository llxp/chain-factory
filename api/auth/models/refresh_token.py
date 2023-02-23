from odmantic import Model, Field
from typing import List


class RefreshToken(Model):
    jti: str
    username: str
    expires_at: int
    created_at: int
    scopes: List[str] = Field(default=[])
    revoked: bool = Field(default=False)
    user_id: str = ''
    display_name: str = ''
    email: str = ''
