from pydantic import BaseModel
from typing import List


class TranslateUsersRequest(BaseModel):
    username: str = ''
    password: str = ''
    user_ids: List[str] = []
