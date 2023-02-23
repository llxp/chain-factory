from typing import List

from pydantic.main import BaseModel


class UserProfile(BaseModel):
    username: str
    user_id: str
    display_name: str
    email: str
    scopes: List[str] = []
