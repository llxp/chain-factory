from io import BytesIO
from sys import __stdout__
from re import sub
from typing import Optional
from typing import Union
from odmantic import AIOEngine
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
# from asyncio import ensure_future

# models
from ..models.mongodb_models import Log

# settings
from ..common.settings import task_log_to_stdout
from ..common.settings import task_log_to_external


class BytesIOWrapper(BytesIO):
    """
    Wrapper for BytesIO to write to stdout and mongodb
    """
    def __init__(
        self,
        task_id: str,
        workflow_id: str,
        mongodb_database: AIOEngine,
        loop: AbstractEventLoop,
    ):
        super().__init__()
        self.task_id = task_id
        self.mongodb_database = mongodb_database
        self.workflow_id = workflow_id
        self.loop = loop

    def read(self, size: Optional[int] = ...) -> bytes:
        return super().read(size)

    def write(self, b: Union[bytes, bytearray]):
        if task_log_to_stdout:
            __stdout__.write(b.decode("utf-8"))
        decoded_log_line = b.decode("utf-8")
        decoded_log_line = self.remove_secrets(decoded_log_line)
        task_log = Log(
            task_id=self.task_id,
            log_line=decoded_log_line,
            workflow_id=self.workflow_id
        )
        if task_log_to_external:
            # dataclass to json and parse to dict
            coroutine = self.mongodb_database.save(task_log)
            # ensure_future(coroutine, loop=self.loop)
            run_coroutine_threadsafe(coroutine, self.loop)
        return super().write(b)

    def remove_secrets(self, string: str) -> str:
        return sub("<s>(.*?)</s>", "REDACTED", string)
