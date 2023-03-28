from asyncio import AbstractEventLoop, Future, get_event_loop, Task as AsyncTask, set_event_loop, wait_for
from typing import Dict, Optional
from json import dumps
from logging import error
from logging import info
from logging import debug
from logging import exception
from logging import warning
from traceback import print_exc
from sys import stdout
from asyncio import sleep
from time import time
from io import BytesIO
from threading import Lock

# direct imports
from .task_thread import TaskThread
from .task_control_thread import TaskControlThread

# wrapper
from .wrapper.interruptable_thread import ThreadAbortException
from .wrapper.redis_client import RedisClient

# models
from .models.mongodb_models import FreeTaskReturnType, Task, Workflow
from .models.mongodb_models import ArgumentType
from .models.mongodb_models import CallbackType
from .models.mongodb_models import TaskRunnerReturnType
from .models.mongodb_models import NormalizedTaskReturnType
from .models.mongodb_models import ErrorCallbackMappingType


class TaskRunner():
    lock = Lock()

    def __init__(
        self,
        name: str,
        callback: CallbackType,
        namespace: str
    ):
        self.callback: CallbackType = callback
        self._name: str = name
        self._task_threads: Dict[str, TaskThread] = {}
        self._task_timeout: int = -1
        self._task_repeat_on_timeout = False
        self._namespace = namespace
        self._error_handlers: ErrorCallbackMappingType = {}

    def set_redis_client(self, redis_client: RedisClient):
        self._redis_client = redis_client

    def update_task_timeout(self, task_timeout: int):
        self._task_timeout = task_timeout

    def update_error_handlers(self, error_handlers: ErrorCallbackMappingType):
        debug(f"updating error handlers to {error_handlers}")
        self._error_handlers = error_handlers

    def update_task_repeat_on_timeout(self, task_repeat_on_timeout: bool):
        self._task_repeat_on_timeout = task_repeat_on_timeout

    @property
    def task_repeat_on_timeout(self):
        return self._task_repeat_on_timeout

    def update_namespace(self, namespace: str):
        self._namespace = namespace

    def running_workflows(self):
        return self._task_threads

    async def run(
        self,
        workflow: Optional[Workflow],
        task: Task,
        buffer: BytesIO,
        loop: Optional[AbstractEventLoop] = get_event_loop()
    ) -> TaskRunnerReturnType:
        workflow_id = task.workflow_id
        arguments = task.arguments
        try:
            debug(f"running task function {self._name} with arguments {dumps(arguments)}")  # noqa: E501
            info(f"running task with workflow_id: {workflow_id}")
            if arguments is None:
                arguments = dict()
            # self.convert_arguments could raise a TypeError
            arguments = self.convert_arguments(arguments)
            with TaskRunner.lock:
                self._task_threads[workflow_id] = self._create_task_thread(arguments, buffer, workflow, task)  # noqa: E501
            # start the task
            with TaskRunner.lock:
                self._task_threads[workflow_id].start()
            # start redis subscribe watcher
            try:
                task_control_thread = TaskControlThread(workflow_id, self._task_threads[workflow_id], self._redis_client, self._namespace)  # noqa: E501
                if loop:
                    print("starting task control thread")
                    set_event_loop(loop)
                    async_task = loop.create_task(task_control_thread.run_async(loop))  # noqa: E501
                    await self._control_task_thread(workflow_id)
                    await async_task
            except ThreadAbortException:
                debug("task control thread aborted")
                pass

            # await self._control_task_thread(workflow_id, None)

            if self._task_threads[workflow_id]._status == 2:
                # wait for task thread to normally exit
                self._task_threads[workflow_id].join()
                info(f"task with workflow id {workflow_id} finished")
            else:
                warning("task aborted or stopped")
            with TaskRunner.lock:
                task_result = self._task_threads[workflow_id].result
                del self._task_threads[workflow_id]
            # parse the result to correctly return a result with arguments
            return TaskRunner._parse_task_output(task_result, arguments)
        except TypeError as e:
            exception(e)
            print_exc(file=stdout)
            del self._task_threads[workflow_id]
            return None

    def _create_task_thread(self, arguments: ArgumentType, buffer: BytesIO, workflow: Optional[Workflow], task: Task):  # noqa: E501
        return TaskThread(self._name, self.callback, arguments, buffer, self._error_handlers, workflow, task)  # noqa: E501

    def _task_finished(self, workflow_id: str):
        return self._task_threads[workflow_id]._status in [2, 3, 4, 5]

    async def _control_task_thread(self, workflow_id: str):  # noqa: E501
        """
        Subscribe to a redis key and listen for control messages
        if there is a 'stop' control message, the thread will be aborted
            => but only, if the 'stop' message
            arrives during the thread's runtime
        """
        start_time = time()
        while True:
            current_time = time()
            elapsed_time = current_time - start_time
            if (
                self._task_timeout != -1 and
                elapsed_time > self._task_timeout
            ):
                self._task_threads[workflow_id].abort_timeout()
                break
            # check, if exited, stopped or aborted
            if self._task_finished(workflow_id):
                break
            await sleep(0.001)

        # cancel the async task
        # if async_task:
        #     async_task.cancel()

    @staticmethod
    def _parse_task_output(
        task_result: FreeTaskReturnType,
        old_arguments: ArgumentType
    ) -> NormalizedTaskReturnType:
        """
        Check, if new parameters have been returned,
        to be able to reschedule the same task with changed parameters
        Returns the result of the task and the arguments,
        either the default arguments or the newly returned arguments
        """
        # tuple means parameters have been returned too
        # result[0] can either be a new task, False or None
        # result[1] is the arguments dict
        if isinstance(task_result, tuple):
            # check, if the first object returned is not None
            # result can be either a new task or False
            if (
                # False, means an error occured
                task_result[0] is False or
                # check for Task type
                isinstance(task_result[0], Task) or
                # check for string type
                isinstance(task_result[0], str) or
                # check for function type
                callable(task_result[0])
            ):
                old_arguments = task_result[1]  # type: ignore
            # override the result to the real result
            # as either Task, False or None
            task_result = task_result[0]
        return task_result, old_arguments

    def convert_arguments(self, arguments: ArgumentType) -> ArgumentType:
        callback_arguments = list(self.callback.__code__.co_varnames)
        callback_types = self.callback.__annotations__
        for argument in arguments:
            if argument in callback_arguments and argument in callback_types:
                if callback_types[argument] == int and isinstance(arguments[argument], str):  # noqa: E501
                    if len(arguments[argument]) > 0:  # type: ignore
                        try:
                            argument_value: str = arguments[argument]  # type: ignore  # noqa: E501
                            arguments[argument] = int(argument_value)
                        except Exception as e:
                            error(e)
        return arguments

    def abort(self, workflow_id: str):
        debug(f"aborting task with workflow id {workflow_id}")
        self._task_threads[workflow_id].abort()

    def stop(self, workflow_id: str):
        debug(f"stopping task with workflow id {workflow_id}")
        self._task_threads[workflow_id].stop()
