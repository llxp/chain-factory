from datetime import datetime
from typing import Dict, List, Optional, Union
from odmantic import AIOEngine, EmbeddedModel, Model, Field

from ..common.generate_random_id import generate_random_id
from ..common.settings import reject_limit


class RegisteredTask(EmbeddedModel):
    name: str
    arguments: Dict[str, str] = {}


class NodeTasks(Model):
    node_name: str
    namespace: Optional[str] = None
    tasks: List[RegisteredTask] = []


class Log(Model):
    __collection__ = "logs"
    log_line: str
    task_id: str
    workflow_id: str


class TaskStatus(Model):
    task_id: str
    namespace: str
    status: str
    created_date: datetime = Field(default_factory=datetime.utcnow)


class Task(EmbeddedModel):
    # required, name of task to start
    name: str
    # required, arguments of task to start
    arguments: Dict[str, Union[str, list, dict]] = {}
    # not required, will be overritten by the task_handler
    received_date: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # not required, should be omitted, when starting a new task
    parent_task_id: Optional[str] = ""
    # not required, should be omitted, when starting a new task
    workflow_id: Optional[str] = ""
    # not required, will be overritten by the task_handler
    task_id: Optional[str] = ""
    # a list of names the task can be started on.
    # Required, can be empty.
    # If empty it will be executed on any of the nodes
    # where the task is registered
    node_names: Optional[List[str]] = []
    # tags to be associated with the new task.
    # Used to query for the workflow logs
    tags: Optional[List[str]] = []
    # not required, should be omitted, when starting a new task
    reject_counter: Optional[int] = 0
    # planned date for timed tasks, can be ommited (optional)
    planned_date: Optional[datetime] = Field(default_factory=datetime.utcnow)

    def workflow_precheck(self):
        return (
            len(self.parent_task_id) <= 0 and
            len(self.workflow_id) <= 0
        )

    async def is_stopped(self, namespace: str, database: AIOEngine):
        workflow_status = await database.find_one(WorkflowStatus, (
            (WorkflowStatus.workflow_id == self.workflow_id) &
            (WorkflowStatus.namespace == namespace)
        ))
        if workflow_status:
            return True
        return False

    def generate_workflow_id(self):
        self.workflow_id = generate_random_id()

    def is_planned_task(self):
        return (
            self.planned_date is not None and
            self.planned_date > datetime.utcnow()
        )

    def increase_rejected(self):
        self.reject_counter = self.reject_counter + 1

    def reset_rejected(self):
        self.reject_counter = 0

    def check_rejected(self):
        return self.reject_counter > reject_limit

    def check_node_filter(self, node_name: str):
        return (
            len(self.node_names) > 0 and
            node_name not in self.node_names
        )

    def generate_task_id(self):
        self.task_id = generate_random_id()

    def update_time(self):
        self.received_date = datetime.utcnow()

    def set_as_parent_task(self):
        self.parent_task_id = self.task_id

    def set_parent_task(self, other_task: "Task"):
        self.parent_task_id = other_task.task_id
        self.workflow_id = other_task.workflow_id
        self.node_names = other_task.node_names

    def has_parent_task(self):
        return len(self.parent_task_id) > 0

    def cleanup_task(self):
        self.task_id = None


class TaskWorkflowAssociation(Model):
    task: Optional[Task] = None
    workflow_id: str
    node_name: str


class WorkflowLog(Model):
    log_lines: List[str] = []
    workflow_id: str
    task_id: str


class Workflow(Model):
    created_date: datetime = Field(default_factory=datetime.utcnow)
    workflow_id: str
    node_name: str
    namespace: str
    tags: List[str] = []


class WorkflowStatus(Model):
    workflow_id: str
    namespace: str
    status: str
    created_date: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    async def get(
        cls: "WorkflowStatus",
        mongodb_client: AIOEngine,
        workflow_id: str,
        namespace: str
    ):
        return await mongodb_client.find_one(cls, (
            (cls.workflow_id == workflow_id) &
            (cls.namespace == namespace)
        ))
