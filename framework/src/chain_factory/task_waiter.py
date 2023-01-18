from .models.mongodb_models import TaskWorkflowAssociation
from .models.mongodb_models import TaskStatus
from .models.mongodb_models import Task
from .wrapper.mongodb_client import MongoDBClient


class TaskWaiter:
    """
    TaskWaiter is a class that is used to wait for tasks to be completed.
    """

    def __init__(self, mongo_client: MongoDBClient):
        """
        Initialize the TaskWaiter class.
        :param mongo_client: MongoDBClient
        """
        self.mongo_client = mongo_client
        self.database = mongo_client.client

    async def wait_for_task_name(self, workflow_id: str, task_name: str, arguments: dict) -> bool:  # noqa: E501
        """
        Wait for a task to be completed.
        :param task_name: str
        :param arguments: dict
        :return: bool
        TODO: Needs to be reimplemented, currently not in use and not working.
        """
        arg_keys = list(arguments.keys())
        query_args = []
        for key in arg_keys:
            query_args.append({f"task.arguments.{key}": arguments[key]})
        # find all running tasks of the current workflow
        task_workflow_association = await self.database.find_one(TaskWorkflowAssociation, {"workflow_id": workflow_id, "task.task_id": task_name, "$and": query_args})  # noqa: E501
        task = task_workflow_association.task if task_workflow_association else None  # noqa: E501
        if task is None:
            return False
        else:
            return await self._wait_for_task(task)

    async def wait_for_task_id(self, task_id: str) -> bool:
        """
        Wait for a task to be completed.
        :param task_id: str
        :return: bool
        """
        task_status = await self.database.find_one(TaskStatus, TaskStatus.task_id == task_id)  # noqa: E501
        if task_status is None:
            return False
        task_workflow_association = await self.database.find_one(TaskWorkflowAssociation, TaskWorkflowAssociation.task.task_id == task_id)  # type: ignore  # noqa: E501
        if task_workflow_association is None:
            return False
        task = task_workflow_association.task if task_workflow_association else None  # noqa: E501
        if task is None:
            return False
        return await self._wait_for_task(task)

    async def _wait_for_task(self, task: Task) -> bool:
        """
        Wait for a task to be completed.
        :param task: Task
        :return: bool
        """
        task_status = await self.database.find_one(TaskStatus, TaskStatus.task_id == task.task_id)  # noqa: E501
        return task_status is not None
