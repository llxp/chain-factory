from logging import warning

from .control_thread import ControlThread
from .common.settings import task_control_channel_redis_key
from .task_thread import TaskThread
from .wrapper.redis_client import RedisClient


class TaskControlThread(ControlThread):
    def __init__(self, workflow_id: str, task_thread: TaskThread, redis_client: RedisClient, namespace: str):  # noqa: E501
        self.task_thread = task_thread

        def stop():
            warning("stopping task")
            self.task_thread.stop()

        def abort():
            warning("aborting task")
            self.task_thread.abort()

        namespace_ = (namespace + "_") if namespace else ""
        control_channel = namespace_ + task_control_channel_redis_key
        ControlThread.__init__(
            self,
            workflow_id=workflow_id,
            control_actions={"stop": stop, "abort": abort},
            redis_client=redis_client,
            control_channel=control_channel,
            thread_name="TaskControlThread"
        )
