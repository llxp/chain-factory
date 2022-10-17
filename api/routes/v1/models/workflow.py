from typing import List, Optional
from odmantic import Model, Field
from datetime import datetime


class Workflow(Model):
    created_date: datetime = Field(default_factory=datetime.utcnow)
    node_name: Optional[str] = ""
    tags: List[str] = []
    workflow_id: Optional[str] = ""
