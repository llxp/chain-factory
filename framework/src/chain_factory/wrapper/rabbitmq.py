from asyncio import AbstractEventLoop, get_event_loop
# from asyncio import get_event_loop
from asyncio import new_event_loop
from asyncio import ensure_future
from dataclasses import dataclass
from logging import debug
from logging import error
from logging import info
import threading
from traceback import print_exc
from sys import stdout
from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Any
from typing import Optional
from typing import Union
from _thread import interrupt_main
from _thread import start_new_thread
from aio_pika import Queue
from aio_pika import connect_robust
from aio_pika import IncomingMessage
from aio_pika import Message as AioPikaMessage
from aio_pika import DeliveryMode
from aio_pika import Channel
from aio_pika import ExchangeType
from aio_pika.connection import Connection
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.exceptions import ChannelInvalidStateError
from aio_pika.exceptions import DuplicateConsumerTag

# settings
from ..common.settings import prefetch_count


@dataclass
class Message():
    body: str
    message: IncomingMessage
    delivery_tag: int


FuncType = Callable[[Message], Awaitable[str]]


class RabbitMQ:
    def __init__(
        self,
        url: str,
        queue_name: str,
        rmq_type: str = "publisher",
        callback: Optional[FuncType] = None,
        queue_options: Dict[str, Any] = {},
        loop: Optional[AbstractEventLoop] = None,
    ):
        self.callback: Optional[FuncType] = callback
        self.queue_name: str = queue_name
        self.rmq_type = rmq_type
        self.url = url
        self.queue_options = queue_options
        self.loop = loop
        self.acked = []
        self.nacked = []
        self._consumer: Optional[_Consumer] = None
        self.sender_channel: Optional[_Consumer] = None
        self.connection: Optional[Connection] = None

    async def init(self):
        if self.loop is None and self.rmq_type == "consumer":
            raise Exception("loop is None and loop is required for consumer")
        self.connection = await RabbitMQ._connect(self.url, loop=self.loop)  # noqa: E501
        if self.rmq_type == "consumer":
            await self.init_consumer()
        await self.init_sender()

    async def init_consumer(self):
        """
        Initializes a new consumer
        """
        if self.connection is None:
            raise Exception("init_consumer: connection is None")
        self._consumer = _Consumer(self.connection, self.queue_name)
        await self._consumer.init()

    async def init_sender(self):
        """
        Initializes the sender channel
        """
        if self.connection is None:
            raise Exception("init_sender: connection is None")
        self.sender_channel = _Consumer(self.connection, self.queue_name, self.queue_options)  # noqa: E501
        await self.sender_channel.init()

    def stop_callback(self):
        self.callback = None

    async def close(self):
        """
        close all consumers and close the connection
        """
        self.callback = None
        if self._consumer:
            await self._consumer.close()
        if self.connection:
            await self.connection.close()

    @staticmethod
    async def _connect(
        url: str,
        loop: Optional[AbstractEventLoop],
    ) -> Connection:
        """
        Connects to an rabbitmq server
        """
        debug(f"opening new RabbitMQ to host {url}")
        url = url + "?heartbeat=20&heartbeat_monitoring=1"
        if not loop:
            loop = get_event_loop()

        print("Connecting with loop")
        connection = await connect_robust(url, timeout=20, loop=loop)
        debug(f"opened new RabbitMQ to host {url}")
        return connection

    async def message_count(self) -> int:
        """
        Retrieves the current count of messages, waiting in the queue
        """
        if self.sender_channel is None:
            raise Exception("sender channel is None")
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
            message_body: str = ""
            if isinstance(message.body, bytes):
                message_body = message.body.decode("utf-8")
            else:
                message_body = message.body
            delivery_tag: int = message.delivery_tag  # type: ignore
            new_message: Message = Message(message_body, message, delivery_tag)  # noqa: E501
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
        if self._consumer is None:
            raise Exception("consumer is None")
        await self._start_consuming(self._consumer)

    async def _start_consuming(self, consumer: "_Consumer"):
        try:
            if consumer is None:
                raise Exception("consumer is None")
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
            if self.sender_channel is None:
                raise Exception("sender_channel is None")
            if self.sender_channel.channel is None:
                raise Exception("sender_channel.channel is None")
            exchange = self.sender_channel.channel.default_exchange
            if exchange is None:
                raise Exception("default exchange is None")
            publish_result = await exchange.publish(new_message, routing_key=self.queue_name)  # noqa: E501
            return publish_result is not None
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
        if self.sender_channel is None:
            raise Exception("sender_channel is None")
        await self.sender_channel.delete_queue()

    async def clear_queue(self):
        """
        Clears the queue
        """
        if self.sender_channel is None:
            raise Exception("sender_channel is None")
        await self.sender_channel.clear_queue()


class _Consumer:
    def __init__(
        self,
        connection: Connection,
        queue_name: str,
        queue_options: Dict[str, Any] = {},
    ):
        self.queue_name = queue_name
        self.connection = connection
        self.queue_options = queue_options
        self.channel: Optional[Channel] = None
        self.queue: Optional[Queue] = None
        self.init_done = False

    async def init(self):
        self.channel = await self._open_channel(self.connection)
        self.queue = await self._declare_queue(self.queue_options)
        self.init_done = True

    @staticmethod
    async def _open_channel(connection: Connection) -> Channel:
        """
        returns the current opened channel of the amqp connection
        """
        debug("opening new Channel on opened connection")
        channel = await connection.channel()
        debug("opened new Channel on opened connection")
        return channel

    async def _declare_queue(self, queue_options: Dict[str, Any] = {}):
        """
        Declare the specified queue
        """
        queue_name = self.queue_name
        debug(f"declaring queue {queue_name}")
        if self.channel is None:
            raise Exception("channel is None")
        # declare an exchange for the queue
        exchange = await self.channel.declare_exchange(name=queue_name, type=ExchangeType.DIRECT, durable=True)  # noqa: E501
        # declare the queue
        queue = await self.channel.declare_queue(name=queue_name, durable=True, arguments=queue_options)  # noqa: E501
        await queue.bind(exchange=exchange, routing_key=queue_name)
        debug(f"declared queue {queue_name}")
        return queue

    async def consume(self, callback: Callable[[IncomingMessage], Awaitable[None]]):  # noqa: E501
        """
        Specify, that this instance should be used to consume messages
        """
        if self.channel is None:
            raise Exception("channel is None")
        await self.channel.set_qos(prefetch_count=prefetch_count)
        if self.queue is None:
            raise Exception("queue is None")
        await self.queue.consume(callback=callback)
        info(f"[{self.queue_name}] [*] Waiting for messages. To exit press CTRL+C")  # noqa: E501

    async def close(self):
        """
        stop consuming on the channel and close the channel
        """
        try:
            if self.channel is None:
                raise Exception("channel is None")
            await self.channel.close()
        except (KeyError, AMQPConnectionError, ChannelInvalidStateError):
            pass

    async def message_count(self) -> int:
        """
        Retrieves the current count of messages, waiting in the queue
        """
        if self.channel is None:
            raise Exception("channel is None")
        res: Queue = await self.channel.declare_queue(
            name=self.queue_name,
            durable=True,
            exclusive=False,
            auto_delete=False,
            passive=True,
        )
        return res.declaration_result.message_count

    async def delete_queue(self):
        """
        Deletes the queue
        """
        if self.channel is None:
            raise Exception("channel is None while deleting queue")
        await self.channel.queue_delete(queue_name=self.queue_name)

    async def clear_queue(self, queue_options: Dict[str, Any] = {}):
        """
        Clears the queue
        """
        await self.delete_queue()
        self.queue = await self._declare_queue(queue_options)


def getPublisher(rabbitmq_url: str, queue_name: str, loop: AbstractEventLoop, queue_options: Dict[str, Any] = {}):  # noqa: E501
    print(threading.get_ident())
    return RabbitMQ(url=rabbitmq_url, queue_name=queue_name, rmq_type="publisher", queue_options=queue_options, loop=loop)  # noqa: E501


def getConsumer(rabbitmq_url: str, queue_name: str, callback: FuncType, loop: AbstractEventLoop):  # noqa: E501
    print("Loop: ", loop)
    print(threading.get_ident())
    return RabbitMQ(url=rabbitmq_url, queue_name=queue_name, rmq_type="consumer", callback=callback, loop=loop)  # noqa: E501
