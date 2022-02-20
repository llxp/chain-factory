from typing import List, Optional
from .credentials import Credentials


class LoginRequest(Credentials):
    scopes: Optional[List[str]] = []
