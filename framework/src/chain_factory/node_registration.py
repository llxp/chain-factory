from inspect import Signature, signature
from typing import Callable, Dict, List

from odmantic import AIOEngine
from .models.mongodb_models import Task, NodeTasks, RegisteredTask
from .task_runner import TaskRunner
from .task_handler import TaskHandler
from .common.settings import unique_hostnames, force_register


class NodeRegistration():
    def __init__(
        self,
        namespace: str,
        database: AIOEngine,
        node_name: str,
        task_handler: TaskHandler
    ):
        self.namespace = namespace
        self.database = database
        self.node_name = node_name
        self.task_handler = task_handler

    async def register_tasks(self):
        """
        Registers all internally registered tasks in the database
        in the form:
            node_name/task_name
        """
        already_registered_node = await self._node_already_registered()
        if already_registered_node is not None:
            if unique_hostnames:  # setting
                await self._raise_node_already_registered()
            if force_register:  # setting
                await self._remove_node_registration()
        await self._register_node()

    async def _register_node(self):
        node_tasks = await self._node_tasks()
        await self.database.save(node_tasks)

    async def _remove_node_registration(self):
        node_registrations = await self._node_already_registered()
        for node_registration in node_registrations:
            await self.database.delete(node_registration)

    async def _raise_node_already_registered(self):
        raise Exception("Existing node name found in redis list, exiting.\nIf this is intentional, set unique_hostnames to False")  # noqa: E501

    async def _node_already_registered(self):
        return await self.database.find(NodeTasks, (
            (NodeTasks.node_name == self.node_name) &
            (NodeTasks.namespace == self.namespace)
        ))

    async def _task_arguments(self, function_signature: Signature):
        """
        Get arguments from task function signature
        """
        return [obj for obj in list(function_signature.parameters) if obj != "self"]  # noqa: E501

    async def _task_argument_types(self, function_signature: Signature):
        """
        Get argument types from task function signature
        """
        return [
            function_signature.parameters[d].annotation.__name__
            if hasattr(function_signature.parameters[d].annotation, "__name__")
            else str(function_signature.parameters[d].annotation)
            for d in function_signature.parameters
        ]

    async def _registered_task(
        self,
        task_name: str,
        callback: Callable[..., Task]
    ):
        """
        Inspect given callback and return a RegisteredTask object
        needed for _node_tasks to assemble the full list of registered tasks
        """
        function_signature = signature(callback)
        argument_names = await self._task_arguments(function_signature)
        argument_types = await self._task_argument_types(function_signature)
        arguments = dict(zip(argument_names, argument_types))
        return RegisteredTask(name=task_name, arguments=arguments)

    async def _node_tasks(self):
        """
        Get all registered tasks on this node
        """
        task_runners: Dict[str, TaskRunner] = self.task_handler.registered_tasks  # noqa: E501
        all_registered_tasks: List[RegisteredTask] = []
        for task_name in task_runners:
            registered_task = await self._registered_task(task_name, task_runners[task_name].callback)  # noqa: E501
            all_registered_tasks.append(registered_task)
        return NodeTasks(node_name=self.node_name, namespace=self.namespace, tasks=all_registered_tasks)  # noqa: E501

    async def register(self):
        await self.register_tasks()
