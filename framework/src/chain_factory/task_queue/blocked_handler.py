from asyncio import AbstractEventLoop
from time import sleep
from logging import info, warning, debug

from .wrapper.rabbitmq import RabbitMQ, Message, getPublisher
from .wrapper.redis_client import RedisClient
from .models.mongodb_models import Task
from .wrapper.list_handler import ListHandler
from .queue_handler import QueueHandler
from .common.settings import wait_time

wait_time = int(wait_time)


class BlockedHandler(QueueHandler):
    """
    Checks, if the task is still on the blocklist and sends them back
    -> to the blocked queue if still on the blocklist
    -> or to the task queue if not on the blocklit anymore
    """

    def __init__(self):
        QueueHandler.__init__(self)

    async def init(
        self,
        rabbitmq_url: str,
        node_name: str,
        task_queue_name: str,
        blocked_queue_name: str,
        block_list_name: str,
        redis_client: RedisClient,
        loop: AbstractEventLoop
    ):
        await QueueHandler.init(self, url=rabbitmq_url, queue_name=blocked_queue_name, loop=loop)  # noqa: E501
        self.node_name = node_name
        self.rabbitmq_sender_task_queue: RabbitMQ = getPublisher(rabbitmq_url=rabbitmq_url, queue_name=task_queue_name)  # noqa: E501
        await self.rabbitmq_sender_task_queue.init()
        self.block_list = ListHandler(list_name=block_list_name, redis_client=redis_client)  # noqa: E501
        await self.block_list.init()

    async def _check_blocklist(self, task: Task, message: Message) -> bool:
        """
        Checks, if the task is still on the blocklist and sends them back
        -> to the blocked queue if still on the blocklist
        -> or to the task queue if not on the blocklit anymore
        """
        task_name = task.name
        blocklist = await self.block_list.get()
        if (
            blocklist is None
            or (blocklist is not None and blocklist.list_items is None)
        ):
            warning(f"blocklist '{self.block_list.list_name}' couldn't be retrieved from redis. Reschedulung task '{task_name}' to queue '{self.queue_name}'")  # noqa: E501
            await self.reschedule(message)
            sleep(wait_time)
            return True
        for blocklist_item in blocklist.list_items:
            if blocklist_item.content in [task_name, "*"] and blocklist_item.name in [self.node_name, "*"]:  # noqa: E501
                debug(f"BlockedHandler:_check_blocklist: task {task_name} is in blocklist")  # noqa: E501
                if blocklist_item.delete:
                    info("task is marked for deletion. deleting/discarding task.")  # noqa: E501
                    return None
                # reschedule task, which is in block list
                info(f"waiting: task {task_name} is not on block list...")
                await self.reschedule(message)
                sleep(wait_time)
                return None
        # send back to task queue, if not on block list
        await self._send_to_task_queue(task, message)
        return None

    async def _send_to_blocked_queue(self, task: Task, message: Message):
        await self.ack(message)
        await self.send_to_queue(task, self.rabbitmq)
        debug("sent back to blocked queue")

    async def _send_to_task_queue(self, task: Task, message: Message):
        await self.ack(message)
        await self.send_to_queue(task, self.rabbitmq_sender_task_queue)
        debug("sent back to task queue")

    async def on_task(self, task: Task, message: Message) -> Task:
        debug("BlockedHandler:on_task: queue_name: " + self.queue_name)
        if task is not None and len(task.name):
            return await self._check_blocklist(task, message)
        else:
            debug("task is empty. discarding task.")
            return None
