from inspect import iscoroutinefunction
from io import BytesIO
from typing import Callable, Optional, Union
from stdio_proxy import redirect_stdout
from stdio_proxy import redirect_stderr
from asyncio import new_event_loop, set_event_loop
from logging import Handler, debug
from logging import exception
from logging import getLogger
from traceback import print_exc
from sys import stdout

# data types
from .models.mongodb_models import ErrorCallbackMappingType, ErrorContext
from .models.mongodb_models import NormalizedTaskReturnType
from .models.mongodb_models import TaskReturnType
from .models.mongodb_models import TaskThreadReturnType
from .models.mongodb_models import Workflow
from .models.mongodb_models import Task

# wrapper
from .wrapper.interruptable_thread import InterruptableThread
from .wrapper.interruptable_thread import ThreadAbortException


class TaskThread(InterruptableThread):
    """
    The thread which actually runs the task
    the output of stdio will be redirected to a buffer
    and later uploaded to the mongodb database
    """

    def __init__(
        self,
        name: str,
        callback: Callable,
        arguments,
        buffer: BytesIO,
        error_handlers: ErrorCallbackMappingType,
        workflow: Optional[Workflow],
        task: Task,
    ):
        InterruptableThread.__init__(self)
        self._name = name
        self._callback = callback
        self._arguments = arguments
        self._error_handlers = error_handlers
        self.result: TaskThreadReturnType = None
        self.workflow = workflow
        self.task = task
        self.async_task = None
        self.future = None
        # current task status
        # 0 means not run
        # 1 means started
        # 2 means finished
        # 3 means stopped
        # 4 means aborted
        self._status = 0
        self._buffer = buffer
        self._log_handler = self.LogHandler(self)

    class LogHandler(Handler):
        def __init__(self, task_thread: "TaskThread"):
            Handler.__init__(self)
            self.task_thread = task_thread

        def emit(self, record):
            message = record.getMessage()
            message_bytes = message.encode(encoding="utf-8")
            self.task_thread._buffer.write(message_bytes)
            self.task_thread._buffer.write(b"\n")

    def run(self):
        try:
            new_loop = new_event_loop()
            set_event_loop(new_loop)
            # redirect stdout and stderr to the buffer
            with redirect_stdout(self._buffer), redirect_stderr(self._buffer):
                root_logger = getLogger()
                try:
                    self._status = 1
                    root_logger.addHandler(self._log_handler)
                    self.result = new_loop.run_until_complete(self._callback(**self._arguments))  # noqa: E501
                    print("result", self.result)
                    root_logger.removeHandler(self._log_handler)
                    self._status = 2
                # catch ThreadAbortException,
                # will be raised if the thread should be forcefully aborted
                except ThreadAbortException as e:
                    debug("TaskThread::run() ThreadAbortException (inner)")
                    exception(e)
                    self.result = ThreadAbortException
                    self._status = 3
                    root_logger.removeHandler(self._log_handler)
                # catch all exceptions to prevent a crash of the node
                except Exception as e:
                    # check if there is a custom error handler for this exception  # noqa: E501
                    self.result = new_loop.run_until_complete(self.try_error_handler(e))  # noqa: E501
                    if self.result is Exception:
                        exception(e)
                        print_exc(file=stdout)
                    self._status = 2
                    root_logger.removeHandler(self._log_handler)
        except ThreadAbortException as e:
            debug("TaskThread::run() ThreadAbortException (outer)")
            exception(e)
            self.result = ThreadAbortException
            self._status = 3
            return

    async def try_error_handler(self, e) -> Union[NormalizedTaskReturnType, TaskReturnType]:  # noqa: E501
        debug(f"Trying to find error handler for exception: {e}, {type(e)}")
        for type_kind, exc_handler in self._error_handlers.items():
            # debug(f"Trying error handler for exception: {e}, {type_kind}")
            if isinstance(e, type_kind):
                debug(f"Found error handler for exception: {e}")
                can_accept_error_context = getattr(exc_handler, "error_context", False)  # noqa: E501
                error_context = ErrorContext()
                if self.workflow is not None:
                    error_context.workflow = self.workflow
                if self.task is not None:
                    error_context.task = self.task
                if iscoroutinefunction(exc_handler):
                    if can_accept_error_context:
                        return await exc_handler(error_context, e, self._name, self._arguments)  # noqa: E501
                    return await exc_handler(e, self._name, self._arguments)  # noqa: E501
                else:
                    if can_accept_error_context:
                        name = self._name
                        arguments = self._arguments
                        return exc_handler(error_context, e, name, arguments)  # type: ignore  # noqa: E501
                    return exc_handler(e, self._name, self._arguments)  # type: ignore  # noqa: E501
        return Exception

    def stop(self):
        self._status = 3
        self.result = KeyboardInterrupt
        super().interrupt()
        super().exit()

    def abort(self):
        self.result = ThreadAbortException
        self._status = 4
        debug("Aborting task thread")
        super().abort()

    def abort_timeout(self):
        self.result = TimeoutError
        self._status = 5
        debug("Aborting task thread due to timeout")
        super().abort()
