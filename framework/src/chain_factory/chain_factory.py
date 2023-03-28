"""
This File has the main class for the chain-factory framework
"""


# from typing import Dict
from asyncio import AbstractEventLoop, CancelledError, get_event_loop, sleep
from asyncio import new_event_loop
from logging import debug, error, exception, warning
from typing import Optional
from typing import Type

# direct imports
from .task_queue_handlers import TaskQueueHandlers

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

    def add_error_context(self):
        """
        Decorator to add workflow context to a task

        - Adds the workflow context to the task
        """
        def wrapper(func):
            func_flag = getattr(func, "error_context", False)
            if not func_flag:
                setattr(func, "error_context", True)
            return func
        return wrapper

    async def shutdown(self):
        """
        Shuts down the framework
        """
        print("Shutting down the framework")
        await self.task_queue_handlers.stop_node()

    def add_error_handler(self, exc_type: Type[Exception], func: ErrorCallbackType):  # noqa: E501
        """
        Adds an error handler to the framework
        """
        self.task_queue_handlers.add_error_handler(exc_type, func)  # noqa: E501

    async def listen(self, loop: Optional[AbstractEventLoop] = None):
        """
        Initialises the queue and starts listening

        - Will be invoked by the `run` method
        """
        if loop is None:
            loop = get_event_loop()
        self._update_task_queue_handlers(loop)
        await self.task_queue_handlers.listen()
        try:
            while True:
                await sleep(1)
        except (KeyboardInterrupt, CancelledError):
            warning("Stopping the task queue")
            await self.task_queue_handlers.stop_node()
            print("Stopped the task queue")
            loop.stop()
            loop.close()
            exit(0)
        except Exception as e:
            error("Error in task queue: ")
            exception(e)
            await self.task_queue_handlers.stop_node()
            print("Stopped the task queue")
            loop.stop()
            loop.close()
            exit(1)

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
            loop.run_until_complete(self.listen(loop))
            if not loop_provided:
                debug("Starting event loop")
                loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
        finally:
            loop.run_until_complete(self.task_queue_handlers.stop_node())
        loop.close()
