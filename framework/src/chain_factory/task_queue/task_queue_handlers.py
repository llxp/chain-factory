from asyncio import AbstractEventLoop
from logging import info, shutdown as shutdown_log
from time import sleep
from typing import Dict

from .credentials_retriever import CredentialsRetriever
from .task_handler import TaskHandler
from .cluster_heartbeat import ClusterHeartbeat
from .client_pool import ClientPool
from .blocked_handler import BlockedHandler
from .wait_handler import WaitHandler
from .node_registration import NodeRegistration
from .task_waiter import TaskWaiter
from .credentials_pool import CredentialsPool
from .common.settings import (
    incoming_block_list_redis_key, wait_block_list_redis_key,
    wait_queue as wait_queue_default, task_queue as task_queue_default,
    incoming_blocked_queue as incoming_blocked_queue_default,
    wait_blocked_queue as wait_blocked_queue_default,
)


class TaskQueueHandlers():
    def __init__(
        self,
        namespace: str,
        namespace_key: str,
        node_name: str,
        endpoint: str,
        username: str,
        password: str,
        worker_count: int,
        task_timeout: int,
        loop: AbstractEventLoop = None,
    ):
        self.node_name = node_name
        self.namespace = namespace
        self.namespace_key = namespace_key
        self.worker_count = worker_count
        self.task_timeout = task_timeout
        self._task_handler: TaskHandler = TaskHandler(
            namespace=self.namespace, node_name=self.node_name)
        self._wait_handler = WaitHandler()
        self._incoming_blocked_handler = BlockedHandler()
        self._wait_blocked_handler = BlockedHandler()
        self.task_queue_clients = ClientPool()
        self._task_waiter: Dict[str, TaskWaiter] = {}
        self._credentials_pool = CredentialsPool(endpoint, username, password, {namespace: namespace_key})  # noqa: E501
        self.loop: AbstractEventLoop = loop
        self.cluster_heartbeat: ClusterHeartbeat = None

    def add_task(self, name: str, callback, repeat_on_timeout: bool = False):  # noqa: E501
        self._task_handler.add_task(name, callback, repeat_on_timeout)

    def namespaced(self, var: str):
        if self.namespace:
            return self.namespace + "_" + var
        return var

    @property
    def task_queue(self):
        # self.namespaced(task_queue_default)
        return task_queue_default

    @property
    def incoming_blocked_queue(self):
        # self.namespaced(incoming_blocked_queue_default)
        return incoming_blocked_queue_default

    @property
    def wait_blocked_queue(self):
        # self.namespaced(wait_blocked_queue_default)
        return wait_blocked_queue_default

    @property
    def wait_queue(self):
        # self.namespaced(wait_queue_default)
        return wait_queue_default

    @property
    def incoming_block_list(self):
        return incoming_block_list_redis_key

    @property
    def wait_block_list(self):
        return wait_block_list_redis_key

    async def redis_client(self):
        return await self.task_queue_clients.redis_client()

    @property
    def mongodb_client(self):
        return self.task_queue_clients.mongodb_client

    async def init(self):
        """
        Init all handlers
        -> wait handler
        -> incoming blocked handler
        -> wait blocked handler
        -> task handler
        -> cluster heartbeat
        """
        # get credentials
        await self._get_credentials()
        # init redis and mongodb connections
        await self.task_queue_clients.init(
            redis_url=self.credentials.redis,
            key_prefix=self.credentials.redis_prefix,
            mongodb_url=self.credentials.mongodb,
            loop=self.loop,
        )
        rabbitmq_url = self.credentials.rabbitmq
        await self._init_wait_handler(rabbitmq_url)
        await self._init_incoming_blocked_handler(rabbitmq_url)
        await self._init_wait_blocked_handler(rabbitmq_url)
        await self._init_task_handler(rabbitmq_url)
        # init cluster heartbeat
        await self._init_cluster_heartbeat()
        # init registration
        await self._init_registration()

    async def _get_credentials(self):
        await self._credentials_pool.init()
        self.credentials = await self._credentials_pool.get_credentials(
            self.namespace, self.namespace_key)

    async def _init_wait_handler(self, rabbitmq_url: str):
        """
        Start the wait handler queue listener
        """
        await self._wait_handler.init(
            rabbitmq_url=rabbitmq_url,
            node_name=self.node_name,
            redis_client=await self.redis_client(),
            queue_name=self.task_queue,
            wait_queue_name=self.wait_queue,
            blocked_queue_name=self.wait_blocked_queue,
            loop=self.loop
        )

    async def _init_incoming_blocked_handler(self, rabbitmq_url: str):
        """
        Init the blocked queue for all blocked tasks,
        which are blocked before even getting to the actual processing
        --> If task is on Blacklist/Blocklist
        --> Node is set to not respond to any of those tasks
        --> Node is in standby mode for those tasks
        """
        await self._incoming_blocked_handler.init(
            rabbitmq_url=rabbitmq_url,
            node_name=self.node_name,
            redis_client=await self.redis_client(),
            task_queue_name=self.task_queue,
            blocked_queue_name=self.incoming_blocked_queue,
            block_list_name=self.incoming_block_list,
            loop=self.loop
        )

    async def _init_wait_blocked_handler(self, rabbitmq_url: str):
        """
        Init the blocked queue listener for all waiting tasks (failed, etc.)
        """
        await self._wait_blocked_handler.init(
            rabbitmq_url=rabbitmq_url,
            node_name=self.node_name,
            redis_client=await self.redis_client(),
            task_queue_name=self.wait_queue,
            blocked_queue_name=self.wait_blocked_queue,
            block_list_name=self.wait_block_list,
            loop=self.loop
        )

    async def _init_task_handler(self, rabbitmq_url: str):
        """
        Init the actual task queue listener
        """
        await self._task_handler.init(
            mongodb_client=self.mongodb_client.client,
            rabbitmq_url=rabbitmq_url,
            redis_client=await self.redis_client(),
            queue_name=self.task_queue,
            wait_queue_name=self.wait_queue,
            blocked_queue_name=self.incoming_blocked_queue,
            loop=self.loop,
        )
        self._task_handler.task_timeout = self.task_timeout
        self._task_handler.update_task_timeout()

    async def _init_cluster_heartbeat(self):
        """
        Init the ClusterHeartbeat
        """
        self.cluster_heartbeat: ClusterHeartbeat = ClusterHeartbeat(
            self.namespace, self.node_name, self.task_queue_clients, self.loop)

    async def listen(self):
        """
        Initialises the queue and starts listening
        """
        await self.init()
        redis_client = await self.redis_client()
        self._task_handler.task_set_redis_client(redis_client)
        await self._node_registration.register()
        self.cluster_heartbeat.start_heartbeat()
        info("listening")
        await self._listen_handlers()

    async def stop_heartbeat(self):
        if self.cluster_heartbeat:
            self.cluster_heartbeat.stop_heartbeat()

    async def stop_node(self):
        await self.stop_listening()
        running_workflows_counter = 0
        task_runner_count = len(self._task_handler.registered_tasks)

        while running_workflows_counter < task_runner_count:
            running_workflows_counter = self.count_running_tasks()
            sleep(0.1)
        if running_workflows_counter >= task_runner_count:
            info("node is dry")
            await self.stop_heartbeat()
            await self.task_queue_clients.close()
            redis_client = await self.redis_client()
            await redis_client.close()
            await self._task_handler.rabbitmq.close()
            await self._wait_handler.rabbitmq.close()
            shutdown_log()

    def count_running_tasks(self):
        running_workflows_counter = 0
        registered_tasks = self._task_handler.registered_tasks
        for registered_task in registered_tasks:
            task_runner = registered_tasks[registered_task]
            if len(task_runner.running_workflows()) <= 0:
                running_workflows_counter = running_workflows_counter + 1
        return running_workflows_counter

    async def _init_registration(self):
        self._node_registration = NodeRegistration(
            self.namespace,
            self.task_queue_clients.mongodb_client.client,
            self.node_name,
            self._task_handler
        )

    async def stop_listening(self):
        info("shutting down node")
        self._task_handler.stop_listening()
        self._wait_handler.stop_listening()
        self._wait_blocked_handler.stop_listening()
        self._incoming_blocked_handler.stop_listening()

    async def _listen_handlers(self):
        """
        Start all handlers to listen
        """
        await self._wait_handler.listen()
        await self._incoming_blocked_handler.listen()
        await self._wait_blocked_handler.listen()
        await self._task_handler.listen()

    async def wait_for_task(
        self,
        namespace: str,
        task_name: str,
        arguments: dict
    ):
        """
        - waits for the task to complete
        """
        credentials: CredentialsRetriever = await self._credentials_pool.get_credentials(namespace)  # noqa: E501
        mongodb_credentials = credentials.mongodb
        try:
            task_waiter: TaskWaiter = self._task_waiter[namespace]
            await task_waiter.wait_for_task_name(task_name, arguments)
        except KeyError:
            self._task_waiter[namespace] = TaskWaiter(self.task_queue_clients.mongodb_client(mongodb_credentials, namespace))  # noqa: E501
            await self._task_waiter[namespace].wait_for_task_name(task_name, arguments)  # noqa: E501
