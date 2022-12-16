from asyncio import AbstractEventLoop, get_event_loop, new_event_loop  # noqa: E501
from dataclasses import dataclass
from logging import debug, error, info
from traceback import print_exc
from sys import stdout
from typing import Callable, Dict, Any, Union
from _thread import interrupt_main
from _thread import start_new_thread
from aio_pika import (
    Queue, connect_robust,
    IncomingMessage, Message as AioPikaMessage,
    DeliveryMode, RobustQueue, Channel
)
from aio_pika.connection import ConnectionType
from aio_pika.exceptions import (
    AMQPConnectionError, AMQPChannelError,
    ChannelInvalidStateError, DuplicateConsumerTag
)
from asyncio import ensure_future

from ..common.settings import prefetch_count


@dataclass
class Message():
    body: str
    message: IncomingMessage
    delivery_tag: int


class RabbitMQ:
    def __init__(
        self,
        url: str,
        queue_name: str,
        rmq_type: str = "publisher",
        callback: Callable[[Message], str] = None,
        queue_options: Dict[str, Any] = None,
        loop: AbstractEventLoop = None,
    ):
        self.callback: Callable[[Message], str] = callback
        self.queue_name: str = queue_name
        self.rmq_type = rmq_type
        self.url = url
        self.queue_options = queue_options
        self.loop = loop
        self.acked = []
        self.nacked = []

    async def init(self):
        self.connection: ConnectionType = await RabbitMQ._connect(self.url, loop=self.loop)  # noqa: E501
        if self.rmq_type == "consumer":
            await self.init_consumer()
        await self.init_sender()

    async def init_consumer(self):
        """
        Initializes a new consumer
        """
        self._consumer = _Consumer(self.connection, self.queue_name)
        await self._consumer.init()

    async def init_sender(self):
        """
        Initializes the sender channel
        """
        self.sender_channel: _Consumer = _Consumer(self.connection, self.queue_name, self.queue_options)  # noqa: E501
        await self.sender_channel.init()

    def stop_callback(self):
        self.callback = None

    async def close(self):
        """
        close all consumers and close the connection
        """
        self.callback = None
        await self._consumer.close()
        await self.connection.close()

    @staticmethod
    async def _connect(
        url: str,
        loop: AbstractEventLoop = None,
    ) -> ConnectionType:
        """
        Connects to an rabbitmq server
        """
        debug(f"opening new RabbitMQ to host {url}")
        if not loop:
            loop = get_event_loop()
        connection = await connect_robust(url, timeout=5, loop=loop)
        debug(f"opened new RabbitMQ to host {url}")
        return connection

    @staticmethod
    async def _queue_exists(self, queue: RobustQueue, queue_name: str):
        """
        Check, if the declared queue has been declared
        """
        try:
            await queue.declare(queue=queue_name, durable=True, passive=True)
            return True
        except (AMQPChannelError, AMQPConnectionError):
            return False

    async def message_count(self) -> int:
        """
        Retrieves the current count of messages, waiting in the queue
        """
        return await self.sender_channel.message_count()

    async def callback_impl(self, message: IncomingMessage):
        """
        callback function, which will be called
        everytime a new message is consumed by the pika/rabbitmq library
        """
        async with message.process(ignore_processed=True):
            debug(f"body: {message.body}")
            if len(message.body) <= 0:
                await message.ack()  # ignore empty messages
                return
            new_message: Message = Message(message.body, message, message.delivery_tag)  # noqa: E501
            if self.callback is not None:
                debug("invoking registered callback method")
                await self._start_callback(new_message)

    def _start_callback_thread(self, new_message: Message):
        def callback_thread(new_message: Message):
            try:
                loop = new_event_loop()
                loop.run_until_complete(self._start_callback(new_message))
            except Exception:
                print_exc()
                error("error in callback thread")
                interrupt_main()
        start_new_thread(callback_thread, (new_message, ))

    async def _start_callback(self, new_message: Message):
        # execute the registered callback
        if self.callback:
            result: str = await self.callback(new_message)
            if result is not None and len(result) > 0:
                # another task has been returned to be scheduled
                send_future = self.send(result)
                await ensure_future(send_future, loop=self.loop)
                debug(f"sent task to same queue, because result is {result}")
            else:
                debug("invoked registered callback method, result is None")

    async def ack(self, message: Message):
        """
        Acknowledges the specified message
        """
        await message.message.ack()

    async def nack(self, message: Message):
        """
        Nacks/Rejects the specified message
        """
        await message.message.nack(requeue=True)

    async def reject(self, message: Message):
        """
        Rejects the specified message
        """
        message.message.reject(requeue=True)

    async def listen(self):
        """
        Starts the rabbitmq consumer/listener
        """
        info(f"starting new consumer for queue {self.queue_name}")
        await self._start_consuming(self._consumer)

    async def _start_consuming(self, consumer: "_Consumer" = None):
        try:
            await consumer.consume(self.callback_impl)
        except Exception:
            error("start_consuming exception")
            print_exc(file=stdout)
            interrupt_main()

    async def send(self, message: str) -> Union[bool, None]:
        """
        Publishes a new task on the queue
        """
        try:
            new_message = self._create_new_message(message)
            return await self.sender_channel.channel.default_exchange.publish(new_message, routing_key=self.queue_name)  # noqa: E501
        except (AMQPConnectionError, ChannelInvalidStateError, DuplicateConsumerTag):  # noqa: E501
            print_exc(file=stdout)
            interrupt_main()

    def _create_new_message(self, message: str):
        return AioPikaMessage(
            body=message.encode("utf-8"),
            content_type="text/plain",
            delivery_mode=DeliveryMode.PERSISTENT,
            headers={}
        )

    async def delete_queue(self):
        """
        Deletes the queue
        """
        await self.sender_channel.delete_queue()

    async def clear_queue(self):
        """
        Clears the queue
        """
        await self.sender_channel.clear_queue()


class _Consumer:
    def __init__(
        self,
        connection: ConnectionType,
        queue_name: str,
        queue_options: Dict[str, Any] = None,
    ):
        self.queue_name = queue_name
        self.connection = connection
        self.queue_options = queue_options
        self.channel: Channel = None
        self.queue: Queue = None

    async def init(self):
        self.channel: Channel = await self._open_channel(self.connection)
        self.queue = await self._declare_queue(self.queue_options)

    @staticmethod
    async def _open_channel(connection: ConnectionType) -> Channel:
        """
        returns the current opened channel of the amqp connection
        """
        debug("opening new Channel on opened connection")
        channel = await connection.channel()
        debug("opened new Channel on opened connection")
        return channel

    async def _declare_queue(self, queue_options: Dict[str, Any]):
        """
        Declare the specified queue
        """
        queue_name = self.queue_name
        debug(f"declaring queue {queue_name}")
        queue = await self.channel.declare_queue(name=queue_name, durable=True, arguments=queue_options)  # noqa: E501
        debug(f"declared queue {queue_name}")
        return queue

    async def consume(self, callback: Callable[[IncomingMessage], str]):
        """
        Specify, that this instance should be used to consume messages
        """
        await self.channel.set_qos(prefetch_count=prefetch_count)
        await self.queue.consume(callback=callback)
        info(f"[{self.queue_name}] [*] Waiting for messages. To exit press CTRL+C")  # noqa: E501

    async def close(self):
        """
        stop consuming on the channel and close the channel
        """
        try:
            await self.channel.close()
        except (KeyError, AMQPConnectionError, ChannelInvalidStateError):
            pass

    async def message_count(self) -> int:
        """
        Retrieves the current count of messages, waiting in the queue
        """
        res: Queue = await self.channel.declare_queue(
            queue=self.queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False,
            passive=True,
        )
        return res["message_count"]

    async def delete_queue(self):
        """
        Deletes the queue
        """
        await self.channel.queue_delete(queue=self.queue_name)

    async def clear_queue(self):
        """
        Clears the queue
        """
        await self.delete_queue()
        self.queue = await self._declare_queue()


def getPublisher(rabbitmq_url: str, queue_name: str, queue_options: Dict[str, Any] = None):  # noqa: E501
    return RabbitMQ(url=rabbitmq_url, queue_name=queue_name, rmq_type="publisher", queue_options=queue_options)  # noqa: E501


def getConsumer(rabbitmq_url: str, queue_name: str, callback: Callable[[Message], str], loop: AbstractEventLoop):  # noqa: E501
    return RabbitMQ(url=rabbitmq_url, queue_name=queue_name, rmq_type="consumer", callback=callback, loop=loop)  # noqa: E501
