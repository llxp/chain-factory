from asyncio import AbstractEventLoop, sleep
from datetime import datetime, timedelta
from logging import info, debug, warning
from amqpstorm import Message

from .wrapper.rabbitmq import RabbitMQ, getPublisher
from .wrapper.redis_client import RedisClient
from .models.mongodb_models import Task
from .wrapper.list_handler import ListHandler
from .queue_handler import QueueHandler
from .common.settings import max_task_age_wait_queue, wait_time, wait_block_list_redis_key  # noqa: E501

wait_time = int(wait_time)
max_task_age_wait_queue = int(max_task_age_wait_queue)


class WaitHandler(QueueHandler):
    def __init__(self):
        QueueHandler.__init__(self)
        self.redis_client = None

    async def init(
        self,
        rabbitmq_url: str,
        node_name: str,
        queue_name: str,
        wait_queue_name: str,
        blocked_queue_name: str,
        redis_client: RedisClient,
        loop: AbstractEventLoop
    ):
        debug("WaitHandler init")
        await QueueHandler.init(self, url=rabbitmq_url, queue_name=wait_queue_name, loop=loop)  # noqa: E501
        self.node_name = node_name
        self.wait_queue_name = wait_queue_name
        await self._init_rabbitmq_task_queue(rabbitmq_url, queue_name)
        await self._init_rabbitmq_blocked(rabbitmq_url, blocked_queue_name)
        await self._init_block_list(redis_client)

    async def _init_block_list(self, redis_client: RedisClient):
        self.block_list = ListHandler(
            list_name=wait_block_list_redis_key,
            redis_client=redis_client
        )
        await self.block_list.init()

    async def _init_rabbitmq_blocked(self, rabbitmq_url: str, blocked_queue_name: str):  # noqa: E501
        self.rabbitmq_blocked: RabbitMQ = getPublisher(rabbitmq_url=rabbitmq_url, queue_name=blocked_queue_name)  # noqa: E501
        await self.rabbitmq_blocked.init()

    async def _init_rabbitmq_task_queue(self, rabbitmq_url: str, queue_name: str):  # noqa: E501
        self.rabbitmq_task_queue: RabbitMQ = getPublisher(rabbitmq_url=rabbitmq_url, queue_name=queue_name)  # noqa: E501
        await self.rabbitmq_task_queue.init()

    async def _check_blocklist(self, task: Task, message: Message):
        task_name = task.name
        blocklist = await self.block_list.get()
        if blocklist is None or (blocklist is not None and blocklist.list_items is None):  # noqa: E501
            warning(f"blocklist '{wait_block_list_redis_key}' couldn't be retrieved from redis. Reschedulung task '{task_name}' to queue '{self.queue_name}'")  # noqa: E501
            await self._reject(message)
            return True
        for blocklist_item in blocklist.list_items:
            if blocklist_item.content in [task_name, "*"] and blocklist_item.name in [self.node_name, "*"]:  # noqa: E501
                # reschedule task, which is in incoming block list
                info(f"task {task_name} is on block list...")
                await self.send_to_queue(task, self.rabbitmq_blocked)
                await sleep(wait_time)
                return True
        return False

    async def _send_to_task_queue(self, task: Task, message: Message):
        await self.ack(message)
        await self.send_to_queue(task, self.rabbitmq_task_queue)
        debug("sent back to task queue")

    async def _reject(self, message: Message):
        debug("waiting...")
        await sleep(wait_time)
        await self.reschedule(message)

    def _seconds_diff(self):
        time_now = datetime.utcnow()
        time_difference = timedelta(seconds=max_task_age_wait_queue)
        return time_now - time_difference

    async def on_task(self, task: Task, message: Message) -> Task:
        if task is not None and len(task.name):
            if await self._check_blocklist(task, message):
                return None
            max_task_age = self._seconds_diff()
            current_task_age = task.received_date
            if current_task_age < max_task_age:
                # task is older then max_task_age
                # reschedule the task to the task_queue
                info(f"reschedulung task to queue: {self.queue_name}")  # noqa: E501
                await self._send_to_task_queue(task, message)
            else:
                await self._reject(message)
        else:
            await self._reject(message)
        return None
