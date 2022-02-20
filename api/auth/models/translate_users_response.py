from pydantic import BaseModel
from typing import List

from .user_information import UserInformation


class TranslateUsersResponse(BaseModel):
    """
    TranslateUsersResponse
    """
    users: List[UserInformation]
