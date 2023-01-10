from io import BytesIO
from .wrapper.interruptable_thread import (
  InterruptableThread, ThreadAbortException
)
from stdio_proxy import redirect_stdout, redirect_stderr
from asyncio import run as run_asyncio
from logging import Handler, exception, getLogger
from traceback import print_exc
from sys import stdout


class TaskThread(InterruptableThread):
    """
    The thread which actually runs the task
    the output of stdio will be redirected to a buffer
    and later uploaded to the mongodb database
    """

    def __init__(self, callback, arguments, buffer: BytesIO):
        InterruptableThread.__init__(self)
        self.callback = callback
        self.arguments = arguments
        # self.result: TaskRunnerReturnType = None
        # current task status
        # 0 means not run
        # 1 means started
        # 2 means finished
        # 3 means stopped
        # 4 means aborted
        self.status = 0
        self.buffer = buffer
        self.log_handler = self.LogHandler(self)

    class LogHandler(Handler):
        def __init__(self, task_thread: "TaskThread"):
            Handler.__init__(self)
            self.task_thread = task_thread

        def emit(self, record):
            self.task_thread.buffer.write(
                record.getMessage().encode(encoding="utf-8"))
            self.task_thread.buffer.write(b"\n")

    def run(self):
        # redirect stdout and stderr to the buffer
        with redirect_stdout(self.buffer), redirect_stderr(self.buffer):
            root_logger = getLogger()
            try:
                self.status = 1
                root_logger.addHandler(self.log_handler)
                self.result = run_asyncio(self.callback(**self.arguments))
                root_logger.removeHandler(self.log_handler)
                self.status = 2
            # catch ThreadAbortException,
            # will be raised if the thread should be forcefully aborted
            except ThreadAbortException as e:
                exception(e)
                self.result = ThreadAbortException
                self.status = 3
                root_logger.removeHandler(self.log_handler)
                return
            # catch all exceptions to prevent a crash of the node
            except Exception as e:
                exception(e)
                print_exc(file=stdout)
                self.result = Exception
                self.status = 2
                root_logger.removeHandler(self.log_handler)
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
