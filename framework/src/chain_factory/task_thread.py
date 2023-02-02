from io import BytesIO
from stdio_proxy import redirect_stdout
from stdio_proxy import redirect_stderr
from asyncio import run as run_asyncio
from logging import Handler
from logging import exception
from logging import getLogger
from traceback import print_exc
from sys import stdout

# data types
from .models.mongodb_models import ErrorCallbackMappingType

# wrapper
from .wrapper.interruptable_thread import InterruptableThread
from .wrapper.interruptable_thread import ThreadAbortException


class TaskThread(InterruptableThread):
    """
    The thread which actually runs the task
    the output of stdio will be redirected to a buffer
    and later uploaded to the mongodb database
    """

    def __init__(self, name, callback, arguments, buffer: BytesIO, error_handlers: ErrorCallbackMappingType):  # noqa: E501
        InterruptableThread.__init__(self)
        self._name = name
        self._callback = callback
        self._arguments = arguments
        self._error_handlers = error_handlers
        # self.result: TaskRunnerReturnType = None
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
            self.task_thread._buffer.write(
                record.getMessage().encode(encoding="utf-8"))
            self.task_thread._buffer.write(b"\n")

    def run(self):
        # redirect stdout and stderr to the buffer
        with redirect_stdout(self._buffer), redirect_stderr(self._buffer):
            root_logger = getLogger()
            try:
                self.status = 1
                root_logger.addHandler(self._log_handler)
                self.result = run_asyncio(self._callback(**self._arguments))
                root_logger.removeHandler(self._log_handler)
                self.status = 2
            # catch ThreadAbortException,
            # will be raised if the thread should be forcefully aborted
            except ThreadAbortException as e:
                exception(e)
                self.result = ThreadAbortException
                self.status = 3
                root_logger.removeHandler(self._log_handler)
                return
            # catch all exceptions to prevent a crash of the node
            except Exception as e:
                for type, exc_handler in self._error_handlers.items():
                    if isinstance(e, type):
                        exc_handler(e, self._name, self._arguments)
                exception(e)
                print_exc(file=stdout)
                self.result = Exception
                self.status = 2
                root_logger.removeHandler(self._log_handler)
                return

    def stop(self):
        self.status = 3
        self.result = KeyboardInterrupt
        super().interrupt()
        super().exit()

    def abort(self):
        self.result = ThreadAbortException
        self.status = 4
        super().abort()

    def abort_timeout(self):
        self.result = TimeoutError
        self.status = 5
        super().abort()
