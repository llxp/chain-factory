from logging import warning

# direct imports
from .control_thread import ControlThread
from .task_thread import TaskThread

# wrapper
from .wrapper.redis_client import RedisClient

# settings
from .common.settings import task_control_channel_redis_key


class TaskControlThread(ControlThread):
    """
    TaskControlThread is a thread that listens to a redis channel for control
    messages. It is used to stop or abort a task.
    ControlThread is a base class that is used to implement the redis broadcast
    listener.
    """
    def __init__(self, workflow_id: str, task_thread: TaskThread, redis_client: RedisClient, namespace: str):  # noqa: E501
        self.task_thread = task_thread

        def stop_task():
            """
            Stops the task thread by calling the stop() method
            on the task thread
            """
            warning("stopping task")
            self.task_thread.stop()

        def abort_task():
            """
            Aborts the task thread by calling the abort() method
            on the task thread
            """
            warning("aborting task")
            self.task_thread.abort()

        # the control channel has the format
        # <namespace>_<task_control_channel_redis_key>
        namespace_ = (namespace + "_") if namespace else ""
        control_channel = namespace_ + task_control_channel_redis_key
        ControlThread.__init__(
            self,
            workflow_id=workflow_id,
            control_actions={"stop": stop_task, "abort": abort_task},
            redis_client=redis_client,
            control_channel=control_channel,
            thread_name="TaskControlThread"
        )
