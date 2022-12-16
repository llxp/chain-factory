from typing import Dict, Any
from json import dumps
from logging import error, info, debug, exception, warning
from traceback import print_exc
from sys import stdout
from time import sleep, time
from io import BytesIO
from threading import Lock

from .models.mongodb_models import Task
from .wrapper.interruptable_thread import ThreadAbortException
from .wrapper.redis_client import RedisClient
from .common.task_return_type import (
    ArgumentType, CallbackType, TaskRunnerReturnType,
    TaskReturnType, NormalizedTaskReturnType
)
from .task_thread import TaskThread
from .task_control_thread import TaskControlThread


class TaskRunner():
    lock = Lock()

    def __init__(
        self,
        name: str,
        callback: CallbackType,
        namespace: str
    ):
        self.callback: CallbackType = callback
        self.name: str = name
        self.task_threads: Dict[str, TaskThread] = {}
        self.task_timeout = None
        self.task_repeat_on_timeout = False
        self.namespace = namespace

    def set_redis_client(self, redis_client: RedisClient):
        self.redis_client = redis_client

    def running_workflows(self):
        return self.task_threads

    async def run(
        self,
        arguments: Dict[str, str],
        workflow_id: str,
        buffer: BytesIO
    ) -> TaskRunnerReturnType:
        try:
            debug(
                f"running task function {self.name} "
                f"with arguments {dumps(arguments)}"
            )
            info(f"running task with workflow_id: {workflow_id}")
            if arguments is None:
                arguments = dict()
            # self.convert_arguments could raise a TypeError
            arguments = self.convert_arguments(arguments)
            with TaskRunner.lock:
                self.task_threads[workflow_id] = self._create_task_thread(
                    arguments, buffer)
            # start the task
            with TaskRunner.lock:
                self.task_threads[workflow_id].start()
            # start redis subscribe watcher
            try:
                task_control_thread = TaskControlThread(
                    workflow_id,
                    self.task_threads[workflow_id],
                    self.redis_client,
                    self.namespace
                )
                task_control_thread.start()
                self._control_task_thread(workflow_id)
            except ThreadAbortException:
                pass

            if self.task_threads[workflow_id].status == 2:
                # wait for task thread to normally exit
                self.task_threads[workflow_id].join()
                info(f"task with workflow id {workflow_id} finished")
            else:
                warning("task aborted or stopped")
            with TaskRunner.lock:
                task_result = self.task_threads[workflow_id].result
                del self.task_threads[workflow_id]
            # parse the result to correctly return a result with arguments
            return TaskRunner._parse_task_output(task_result, arguments)
        except TypeError as e:
            exception(e)
            print_exc(file=stdout)
            del self.task_threads[workflow_id]
            return None

    def _create_task_thread(
        self,
        arguments: Dict[str, str],
        buffer: BytesIO
    ):
        return TaskThread(
            self.callback,
            arguments,
            buffer
        )

    def _task_finished(self, workflow_id: str):
        return self.task_threads[workflow_id].status in [2, 3, 4, 5]

    def _control_task_thread(self, workflow_id: str):
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
                self.task_timeout is not None and
                elapsed_time > self.task_timeout
            ):
                self.task_threads[workflow_id].abort_timeout()
                break
            # check, if exited, stopped or aborted
            if self._task_finished(workflow_id):
                break
            sleep(0.001)

    @staticmethod
    def _parse_task_output(
        task_result: TaskReturnType,
        arguments: Dict[str, str]
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
                arguments = task_result[1]
            # override the result to the real result
            # as either Task, False or None
            task_result = task_result[0]
        return task_result, arguments

    def convert_arguments(self, arguments: ArgumentType) -> Dict[str, Any]:
        callback_arguments = list(self.callback.__code__.co_varnames)
        callback_types = self.callback.__annotations__
        for argument in arguments:
            if argument in callback_arguments and argument in callback_types:
                if (
                    callback_types[argument] == int and
                    type(arguments[argument]) == str and
                    len(arguments[argument]) > 0
                ):
                    try:
                        arguments[argument] = int(arguments[argument])
                    except Exception as e:
                        error(e)
        return arguments

    def abort(self, workflow_id: str):
        self.task_threads[workflow_id].abort()

    def stop(self, workflow_id: str):
        self.task_threads[workflow_id].stop()
