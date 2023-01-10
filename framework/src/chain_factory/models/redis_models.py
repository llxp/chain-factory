from datetime import datetime
from pydantic import BaseModel, Field


class Heartbeat(BaseModel):
    node_name: str
    namespace: str
    last_time_seen: datetime = Field(default_factory=datetime.utcnow)


class TaskControlMessage(BaseModel):
    workflow_id: str
    command: str


class TaskLogStatus(BaseModel):
    task_id: str
    status: int = 0


class TaskStatus(BaseModel):
    task_id: str
    status: str
    finished_date: datetime = Field(default_factory=datetime.utcnow)


class WorkflowStatus(BaseModel):
    workflow_id: str
    status: int = 0
