from pydantic import BaseModel
from typing import Dict, Union

from .user_information import UserInformation


class TranslateUsersResponse(BaseModel):
    """
    TranslateUsersResponse
    """
    users: Union[UserInformation, Dict[str, UserInformation]]
