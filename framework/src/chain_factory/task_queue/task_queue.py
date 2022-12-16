from typing import Dict
from asyncio import AbstractEventLoop, new_event_loop

from .task_starter import TaskStarter
from .task_queue_handlers import TaskQueueHandlers
# import the settings
from .common.settings import \
    worker_count as default_worker_count, \
    task_timeout as default_task_timeout, \
    task_repeat_on_timeout as default_task_repeat_on_timeout, \
    namespace as default_namespace, \
    namespace_key as default_namespace_key
from .common.generate_random_id import generate_random_id
from .credentials_retriever import CredentialsRetriever


class TaskQueue():
    """
    Main Class for the chain-factory framework
    """

    def __init__(
        self,
        endpoint: str,
        username: str,
        password: str,
        namespace: str = default_namespace,
        namespace_key: str = default_namespace_key,
        worker_count: int = default_worker_count,
        task_timeout: int = default_task_timeout,
        task_repeat_on_timeout: bool = default_task_repeat_on_timeout,
        node_name: str = generate_random_id()
    ):
        """
        Initialises chain-factory framework
        using the default values from the settings
        """
        self.node_name = node_name
        self.worker_count = worker_count
        # task timeout
        self.task_timeout = task_timeout
        self.task_repeat_on_timeout = task_repeat_on_timeout
        # namespace
        self.namespace = namespace
        self.namespace_key = namespace_key
        # task starter
        self._task_starter: Dict[str, TaskStarter] = {}
        self.task_queue_handlers: TaskQueueHandlers = TaskQueueHandlers(
            namespace=self.namespace,
            namespace_key=self.namespace_key,
            node_name=self.node_name,
            endpoint=endpoint,
            username=username,
            password=password,
            worker_count=self.worker_count,
            task_timeout=self.task_timeout,
        )

    async def start_new_task(
        self,
        task_name: str,
        arguments: dict,
        namespace: str = None,
        namespace_key: str = None
    ):
        """
        starts a new task
        """
        if namespace is None:
            namespace = self.namespace
        if namespace_key is None:
            namespace_key = self.namespace_key
        credentials: CredentialsRetriever = \
            await self.task_queue_handlers._credentials_pool.get_credentials(
                namespace, namespace_key)
        rabbitmq_url = credentials.rabbitmq()
        try:
            await self._task_starter[namespace].start_task(
                task_name, arguments)
        except KeyError:
            self._task_starter[namespace] = TaskStarter(
                namespace=namespace,
                rabbitmq_url=rabbitmq_url,
            )
            self._task_starter[namespace].start_task(
                task_name, arguments)

    async def wait_for_task(
        self,
        namespace: str,
        task_name: str,
        arguments: dict
    ):
        """
        waits for the task to complete
        """
        self.task_queue_handlers.wait_for_task(namespace, task_name, arguments)

    def task(
        self,
        name: str = "",
        repeat_on_timeout: bool = default_task_repeat_on_timeout
    ):
        """
        Decorator to register a new task in the framework
        """
        def wrapper(func):
            temp_name = name
            if len(temp_name) <= 0:
                # get the function name as string
                temp_name = func.__name__
            # register the function
            # using the function name
            self.task_queue_handlers.add_task(
                temp_name, func, repeat_on_timeout)
            return func
        return wrapper

    def add_task(
        self,
        func,
        name: str = "",
        repeat_on_timeout: bool = default_task_repeat_on_timeout
    ):
        """
        Method to add tasks, which cannot be added using the decorator
        Registers a new task in the framework
        """
        outer_wrapper = self.task(name, repeat_on_timeout)
        outer_wrapper(func)

    async def listen(self, loop: AbstractEventLoop = None):
        """
        Initialises the queue and starts listening
        """
        self._update_task_queue_handlers(loop)
        await self.task_queue_handlers.listen()

    def _update_task_queue_handlers(self, loop: AbstractEventLoop = None):
        """
        Updates the task queue handlers properties
        with the values from the task queue
        """
        self.task_queue_handlers.loop = loop
        self.task_queue_handlers.worker_count = self.worker_count
        self.task_queue_handlers.namespace = self.namespace
        self.task_queue_handlers.node_name = self.node_name
        self.task_queue_handlers.task_timeout = self.task_timeout
        self.task_queue_handlers.namespace_key = self.namespace_key
        self.task_queue_handlers.node_name = self.node_name

    def run(self):
        """
        Runs the task queue
        - Starts the event loop
        - Starts listening for tasks
        and stops the event loop on keyboard interrupt
        """
        try:
            loop = new_event_loop()
            loop.create_task(self.listen(loop))
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
        finally:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
