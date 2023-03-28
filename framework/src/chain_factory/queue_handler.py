from abc import abstractmethod
from asyncio import AbstractEventLoop
from datetime import datetime
from logging import error
from logging import debug
from traceback import print_exc
from sys import exit
from sys import stderr
from typing import Union
from aio_pika.exceptions import AMQPConnectionError

# decorators
from .decorators.parse_catcher import parse_catcher

# wrapper
from .wrapper.rabbitmq import RabbitMQ
from .wrapper.rabbitmq import Message
from .wrapper.rabbitmq import getConsumer

# models
from .models.mongodb_models import Task


class QueueHandler:
    """
    Base Class for the TaskQueue,
    handles the rabbitmq task queue dispatch logic
    """
    def __init__(self):
        self.rabbitmq: Union[RabbitMQ, None] = None

    async def init(self, url: str, queue_name: str, loop: AbstractEventLoop):
        """
        Separate init logic to be able to use lazy initialisation
        """
        self.queue_name = queue_name
        await self._connect(url=url, loop=loop)

    def stop_listening(self):
        if self.rabbitmq:
            self.rabbitmq.stop_callback()

    async def close(self):
        if self.rabbitmq:
            print("Closing queue handler")
            await self.rabbitmq.close()

    async def _connect(self, url: str, loop: AbstractEventLoop):
        """
        Connects to rabbitmq
        """
        try:
            self.rabbitmq = getConsumer(rabbitmq_url=url, queue_name=self.queue_name, callback=self._on_message, loop=loop)  # noqa: E501
            await self.rabbitmq.init()
        except AMQPConnectionError:
            print_exc(file=stderr)
            exit(1)

    async def listen(self):
        """
        starts listening on the queue
        """
        if self.rabbitmq is None:
            raise ValueError("RabbitMQ is not initialized")
        await self.rabbitmq.listen()

    async def reschedule(self, message: Message):
        """
        Reschedules or rather rejects the message
        """
        await self.nack(message=message)

    @staticmethod
    def _now():
        """
        returns the current time with timezone
        """
        return datetime.utcnow()

    @staticmethod
    async def send_to_queue(task: Task, rabbitmq: Union[RabbitMQ, None]):
        """
        Send a task to the specified queue
        """
        task.received_date = QueueHandler._now()
        if rabbitmq is None:
            raise ValueError("RabbitMQ is not initialized")
        return await rabbitmq.send(message=task.json())

    async def ack(self, message: Message):
        """
        Acknowledges the specified message
        """
        if self.rabbitmq is None:
            raise ValueError("RabbitMQ is not initialized")
        await self.rabbitmq.ack(message=message)

    async def nack(self, message: Message):
        """
        Rejects the specified message
        """
        if self.rabbitmq is None:
            raise ValueError("RabbitMQ is not initialized")
        await self.rabbitmq.nack(message=message)

    @abstractmethod
    async def on_task(self, task: Task, message: Message) -> Union[None, Task]:
        """
        abstract method for the overriding clas,
        will be invoked, when a new task comes in
        """
        error(
            "Error: on_task on queue_handler has been called. "
            "Please implement the on_task method "
            "in the derived class of queue_handler"
        )
        raise NotImplementedError(
            "Error: on_task on queue_handler has been called. "
            "Please implement the on_task method in the derived "
            "class of queue_handler"
        )

    async def _on_message(self, message: Message) -> str:
        """
        method will be invoked by the amqp library, when a new message comes in
        """
        debug("callback_impl in queue_handler called")
        # parse the message body to Task
        task = self._parse_json(body=message.body)
        task_json = task.json() if task is not None else "None"
        debug(f"task: {task_json}")
        return await self._on_message_check_task(task, message)

    async def _on_message_check_task(self, task: Union[Task, None], message: Message):  # noqa: E501
        if task is not None and len(task.name) > 0:
            return await self._on_task(task=task, message=message)
        else:
            return self._on_task_error(message=message)

    @staticmethod
    @parse_catcher((AttributeError, TypeError, Exception))
    def _parse_json(body: str) -> Union[None, Task]:
        if len(body) > 0:
            return Task.parse_raw(body)
        else:
            return None

    async def _on_task(self, task: Task, message: Message) -> str:
        """
        method will be invoked by _on_message, when a new task comes in
        checks the return value
        and returns them after logging to the amqp library
        """
        debug("on_task will be called")
        result = await self.on_task(task, message)
        return self._on_task_check_task_result(result)

    def _on_task_check_task_result(self, result: Union[Task, None]):
        if result is None:
            return self._on_none_task_result()
        else:
            return self._on_task_result(result)

    def _on_task_result(self, result: Task):
        result_json = result.json()
        debug(f"result: {result_json}")
        # return the result as json to the queue
        return result_json

    def _on_none_task_result(self):
        debug("result: None")
        return ""

    def _on_task_error(self, message: Message) -> str:
        """
        will be invoked,
        when an error occured during parsing the message to a task
        """
        error(f"Error, message is not parsable. Body: {message.body}")
        return ""
