from pydantic import BaseModel
from typing import List


class NewTaskRequest(BaseModel):
    arguments: dict = {}
    tags: List[str] = []


class TaskCreatedResponse(BaseModel):
    message: str
