from asyncio import AbstractEventLoop
from logging import warning
from typing import Dict
from pymongo.errors import CollectionInvalid

from .models.mongodb_models import (
    TaskWorkflowAssociation, Workflow,
    Log, WorkflowStatus
)
from .wrapper.mongodb_client import MongoDBClient
from .wrapper.redis_client import RedisClient
from .wrapper.rabbitmq import RabbitMQ


class ClientPool():
    def __init__(
        self,
    ):
        self.mongodb_client: MongoDBClient = None
        self.redis_clients: Dict[str, RedisClient] = {}
        self.rabbitmq_clients: Dict[str, RabbitMQ] = {}
        self.loop: AbstractEventLoop = None

    async def init(
        self,
        redis_url: str,
        key_prefix: str,
        mongodb_url: str,
        loop: AbstractEventLoop,
    ):
        """
        - initialises the redis client
        - initialises the mongodb client
        """
        self.redis_clients["default"] = await self._init_redis(redis_url, key_prefix)  # noqa: E501
        self.mongodb_client: MongoDBClient = await self._init_mongodb(mongodb_url)  # noqa: E501
        self.loop = loop

    async def redis_client(
        self,
        redis_url: str = "default",
        key_prefix: str = ""
    ) -> RedisClient:
        """
        return a redis client specific to the given redis url
        if no redis url is given, return the default redis client
        if no default redis client exists,
            create a new one with the given redis url
        """
        if redis_url not in self.redis_clients:
            self.redis_clients[redis_url] = await self._init_redis(
                redis_url, key_prefix)
        return self.redis_clients[redis_url]

    async def _init_mongodb(self, mongodb_url: str) -> MongoDBClient:
        """
        returns a new mongodb client object
        """
        client = MongoDBClient(mongodb_url)
        await client.check_connection()
        await self._init_mongodb_collections(client)
        return client

    async def _init_redis(
        self,
        redis_url: str,
        key_prefix: str
    ) -> RedisClient:
        """
        returns a new redis client object
        """
        return RedisClient(
            redis_url=redis_url,
            key_prefix=key_prefix,
            loop=self.loop
        )

    async def _init_mongodb_collections(self, client: MongoDBClient):
        """
        initialises the mongodb collections
        """
        motor_client = client.client
        try:
            await motor_client.database.create_collection(
                Workflow.__collection__,
            )
            await motor_client.database.create_collection(
                TaskWorkflowAssociation.__collection__,
            )
            await motor_client.database.create_collection(
                Log.__collection__,
            )
            await motor_client.database.create_collection(
                WorkflowStatus.__collection__,
            )
        except CollectionInvalid as e:
            warning(e)
        workflow_collection = motor_client.get_collection(Workflow)
        await workflow_collection.create_index("workflow_id")
        twa_collection = motor_client.get_collection(TaskWorkflowAssociation)
        await twa_collection.create_index("workflow_id")
        log_collection = motor_client.get_collection(Log)
        await log_collection.create_index("task_id")

    async def close(self):
        """
        closes all the clients
        """
        for redis_client in self.redis_clients.values():
            if redis_client:
                await redis_client.close()
        if self.mongodb_client:
            await self.mongodb_client.close()
        for rabbitmq_client in self.rabbitmq_clients.values():
            rabbitmq_client.stop_callback()
            if rabbitmq_client:
                await rabbitmq_client.close()
