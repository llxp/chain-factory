from pydantic import BaseModel
from typing import List


class TranslateUsersRequest(BaseModel):
    user_ids: List[str] = []
