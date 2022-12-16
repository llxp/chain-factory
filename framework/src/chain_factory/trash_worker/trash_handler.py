from logging import debug
from ..task_queue.queue_handler import QueueHandler
from amqpstorm import Message
from typing import Union

from ..task_queue.models.mongodb_models import Task
from ..task_queue.wrapper.redis_client import RedisClient


class TrashHandler(QueueHandler):
    def __init__(
        self,
        queue_name: str,
        rabbitmq_url: str,
        redis_url: str,
        namespace: str = None,
        redis_key: str = "trash_queue_output"
    ):
        super().__init__(self)
        self.rabbitmq_url = rabbitmq_url
        self.redis_client = RedisClient(redis_url=redis_url)
        self.redis_key = redis_key
        self.namespace = namespace
        self.queue_name = queue_name

    async def init(self):
        await super().init(
            url=self.rabbitmq_url,
            queue_name=self.queue_name,
        )

    async def on_task(self, task: Task, message: Message) -> Union[None, Task]:
        task_json = task.json()
        debug(task_json)
        ns = self.namespace + "_" if self.namespace else ""
        self.redis_client.rpush(ns + self.redis_key, task_json)
