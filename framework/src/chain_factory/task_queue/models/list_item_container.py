from typing import List, Optional
from pydantic import BaseModel


class ListItem(BaseModel):
    name: str = ""
    content: str = ""
    delete: Optional[bool] = False


class ListItemContainer(BaseModel):
    list_items: List[ListItem] = []
