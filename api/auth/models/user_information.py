from typing import List

from pydantic.main import BaseModel


class UserInformation(BaseModel):
    user_id: str
    username: str
    display_name: str
    email: str
    groups: List[str] = []
