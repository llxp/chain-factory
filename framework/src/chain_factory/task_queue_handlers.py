from asyncio import AbstractEventLoop
from logging import info
from logging import shutdown as shutdown_log
from time import sleep
from typing import Optional
from typing import Union

# direct imports
from .client_pool import ClientPool
from .node_registration import NodeRegistration
from .credentials_pool import CredentialsPool
from .cluster_heartbeat import ClusterHeartbeat
# queue handlers
from .task_handler import TaskHandler

# models
from .models.mongodb_models import ErrorCallbackType

# settings
from .common.settings import wait_queue as wait_queue_default
from .common.settings import task_queue as task_queue_default
from .common.settings import incoming_blocked_queue as incoming_blocked_queue_default  # noqa: E501


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
        loop: Optional[AbstractEventLoop] = None,
    ):
        self.node_name = node_name
        self.namespace = namespace
        self.namespace_key = namespace_key
        self.worker_count = worker_count
        self.task_timeout = task_timeout
        self._task_handler: TaskHandler = TaskHandler(self.namespace, self.node_name)  # noqa: E501
        self.client_pool = ClientPool()
        self._credentials_pool = CredentialsPool(endpoint, username, password, {namespace: namespace_key})  # noqa: E501
        self.loop: Optional[AbstractEventLoop] = loop
        self.cluster_heartbeat: Union[ClusterHeartbeat, None] = None

    def add_task(self, name: str, callback, repeat_on_timeout: bool = False):  # noqa: E501
        self._task_handler.add_task(name, callback, repeat_on_timeout)

    def add_error_handler(self, exc_type, callback: ErrorCallbackType):  # noqa: E501
        self._task_handler.add_error_handler(exc_type, callback)

    def namespaced(self, var: str):
        if self.namespace:
            return self.namespace + "_" + var
        return var

    @property
    def task_queue(self):
        return task_queue_default

    @property
    def incoming_blocked_queue(self):
        return incoming_blocked_queue_default

    @property
    def wait_queue(self):
        return wait_queue_default

    async def redis_client(self):
        return await self.client_pool.redis_client(loop=self.loop)

    @property
    def mongodb_client(self):
        return self.client_pool.mongodb_client

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
        if self.loop is None:
            raise Exception("No loop provided")
        # init redis and mongodb connections
        await self.client_pool.init(
            redis_url=self.credentials.redis,
            key_prefix=self.credentials.redis_prefix,
            mongodb_url=self.credentials.mongodb,
            loop=self.loop,
        )
        rabbitmq_url = self.credentials.rabbitmq
        await self._init_task_handler(rabbitmq_url)
        # init cluster heartbeat
        await self._init_cluster_heartbeat()
        # init registration
        await self._init_registration()

    async def _get_credentials(self):
        await self._credentials_pool.init()
        self.credentials = await self._credentials_pool.get_credentials(self.namespace, self.namespace_key)  # noqa: E501

    async def _init_task_handler(self, rabbitmq_url: str):
        """
        Init the actual task queue listener
        """
        if self.loop is None:
            raise Exception("No loop provided")
        if self.mongodb_client is None:
            raise Exception("No mongodb client provided")
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
        self._task_handler.update_error_handlers()

    async def _init_cluster_heartbeat(self):
        """
        Init the ClusterHeartbeat
        """
        if self.loop is None:
            raise Exception("No loop provided")
        self.cluster_heartbeat = ClusterHeartbeat(self.namespace, self.node_name, self.client_pool, self.loop)  # noqa: E501

    async def listen(self):
        """
        Initialises the queue and starts listening
        """
        await self.init()
        redis_client = await self.redis_client()
        self._task_handler.task_set_redis_client(redis_client)
        await self._node_registration.register()
        info("listening")
        await self._listen_handlers()
        if self.cluster_heartbeat:
            self.cluster_heartbeat.start_heartbeat()

    async def stop_heartbeat(self):
        if self.cluster_heartbeat:
            self.cluster_heartbeat.stop_heartbeat()
            print("stopped heartbeat")

    async def stop_node(self):
        print("stopping node")
        self.stop_listening()
        running_workflows_counter = 0
        task_runner_count = len(self._task_handler.registered_tasks)

        while running_workflows_counter < task_runner_count:
            running_workflows_counter = self.count_running_tasks()
            sleep(0.1)
        if running_workflows_counter >= task_runner_count:
            info("node is dry")
            await self.stop_heartbeat()
            print("stopped heartbeat")
            await self.client_pool.close()
            await self._task_handler.close()
            shutdown_log()
            print("node stopped")

    def count_running_tasks(self):
        running_workflows_counter = 0
        registered_tasks = self._task_handler.registered_tasks
        for registered_task in registered_tasks:
            task_runner = registered_tasks[registered_task]
            if len(task_runner.running_workflows()) <= 0:
                running_workflows_counter = running_workflows_counter + 1
        return running_workflows_counter

    async def _init_registration(self):
        if self.mongodb_client is None:
            raise Exception("No mongodb client provided")
        self._node_registration = NodeRegistration(
            self.namespace,
            self.mongodb_client.client,
            self.node_name,
            self._task_handler
        )

    def stop_listening(self):
        info("shutting down node")
        self._task_handler.stop_listening()

    async def _listen_handlers(self):
        """
        Start all handlers to listen
        """
        await self._task_handler.listen()
