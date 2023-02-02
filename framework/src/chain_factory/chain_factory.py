"""
This File has the main class for the chain-factory framework
"""


# from typing import Dict
from asyncio import AbstractEventLoop
from asyncio import new_event_loop
from logging import debug
from typing import Optional
from typing import Type

# direct imports
# from .task_starter import TaskStarter
from .task_queue_handlers import TaskQueueHandlers
# from .credentials_retriever import CredentialsRetriever

# data types
from .models.mongodb_models import ErrorCallbackType

# settings
from .common.settings import worker_count as default_worker_count
from .common.settings import task_timeout as default_task_timeout
from .common.settings import task_repeat_on_timeout as default_task_repeat_on_timeout  # noqa: E501
from .common.settings import namespace as default_namespace
from .common.settings import namespace_key as default_namespace_key


class ChainFactory():
    """
    Main Class for the chain-factory framework

    This class is used
        to initialize the framework by creating a new instance of the class
        to register tasks and
        to start listening
    """

    def __init__(
        self,
        endpoint: str,
        username: str,
        password: str,
        node_name: str,
        namespace: str = default_namespace,
        namespace_key: str = default_namespace_key,
        worker_count: int = default_worker_count,
        task_timeout: int = default_task_timeout,
        task_repeat_on_timeout: bool = default_task_repeat_on_timeout,
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
        # self._task_starter: Dict[str, TaskStarter] = {}
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

    # async def start_new_task(
    #     self,
    #     task_name: str,
    #     arguments: dict,
    #     namespace: str = "",
    #     namespace_key: str = ""
    # ):
    #     """
    #     starts a new task by name
    #     (can be e.g. used
    #     to start a task of a different namespace)
    #     """
    #     if namespace is None:
    #         namespace = self.namespace
    #     if namespace_key is None:
    #         namespace_key = self.namespace_key
    #     credentials: CredentialsRetriever = \
    #         await self.task_queue_handlers._credentials_pool.get_credentials(
    #             namespace, namespace_key)
    #     rabbitmq_url = credentials.rabbitmq
    #     try:
    #         await self._task_starter[namespace].start_task(
    #             task_name, arguments)
    #     except KeyError:
    #         self._task_starter[namespace] = TaskStarter(
    #             namespace=namespace,
    #             rabbitmq_url=rabbitmq_url,
    #         )
    #         await self._task_starter[namespace].start_task(task_name, arguments)  # noqa: E501

    # async def wait_for_task(
    #     self,
    #     namespace: str,
    #     task_name: str,
    #     arguments: dict
    # ):
    #     """
    #     waits for a task to complete
    #     TODO: Needs to be reimplemented, as the current logic is not working, so the method is commented out  # noqa: E501
    #     """
    #     await self.task_queue_handlers.wait_for_task(namespace, task_name, arguments)  # noqa: E501

    def task(self, name: str = "", repeat_on_timeout: bool = default_task_repeat_on_timeout):  # noqa: E501
        """
        Decorator to register a new task in the framework

        - Registers a new task in the framework internally
            - using the function name as the task name
            - using the function as the task handler,
              which will be wrapped internally in a TaskRunner class
        - also adds a special `.s` method to the function,
          which can be used to start the function as a task
          from inside another task (for chaining of tasks)
        - registration in mongodb will be done during the initialisation phase
        """
        def wrapper(func):
            temp_name = name
            if len(temp_name) <= 0:
                # get the function name as string
                temp_name = func.__name__
            # register the function
            # using the function name
            self.task_queue_handlers.add_task(temp_name, func, repeat_on_timeout)  # noqa: E501
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

        - Calls the `task` decorator
        """
        outer_wrapper = self.task(name, repeat_on_timeout)
        outer_wrapper(func)

    def add_error_handler(self, exc_type: Type[Exception], func: ErrorCallbackType):  # noqa: E501
        """
        Adds an error handler to the framework
        """
        self.task_queue_handlers.add_error_handler(exc_type, func)  # noqa: E501

    async def listen(self, loop: AbstractEventLoop):
        """
        Initialises the queue and starts listening

        - Will be invoked by the `run` method
        """
        self._update_task_queue_handlers(loop)
        await self.task_queue_handlers.listen()

    def _update_task_queue_handlers(self, loop: AbstractEventLoop):
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

    def run(self, loop: Optional[AbstractEventLoop] = None):
        """
        Runs the task queue:

        - Starts a new event loop or uses a provided one
        - Starts listening for tasks
        - and stops the event loop on keyboard interrupt
        """
        loop_provided = True
        if loop is None:
            loop = new_event_loop()
            loop_provided = False
        try:
            loop.create_task(self.listen(loop))
            if not loop_provided:
                debug("Starting event loop")
                loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
        finally:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
