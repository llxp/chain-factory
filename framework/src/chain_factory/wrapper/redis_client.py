from asyncio import AbstractEventLoop
from asyncio import ensure_future
from asyncio import wait
from logging import debug
from redis.client import PubSub
from redis.client import StrictRedis
from redis.exceptions import ConnectionError
# from threading import Lock
from typing import Dict
from typing import Any
from typing import List
from typing import Optional
from redis_sentinel_url import connect as rsu_connect

connection_pools: Dict[str, List[StrictRedis]] = {}


class RedisClient():
    """
    Wrapper class around the redis python library
    """

    def __init__(
        self,
        redis_url: str,
        key_prefix: str,
        loop: AbstractEventLoop,
    ):
        debug(f"RedisClient: {redis_url}")
        self.loop = loop
        self._connection: StrictRedis = self._get_connection(redis_url=redis_url)  # noqa: E501
        self._key_prefix = key_prefix
        self._pubsub_connection: PubSub = self._get_pubsub_connection()
        # self.mutex = Lock()

    @property
    def key_prefix(self) -> str:
        return self._key_prefix

    def prefixed(self, key) -> str:
        return f"{self.key_prefix}_{key}"

    def _get_connection(self, redis_url: str) -> StrictRedis:
        """
        Create a new connection, if not already found in the connection pool
        """
        global connection_pools
        client = self._connect(redis_url)
        if (redis_url not in connection_pools):
            connection_pools[redis_url] = [client]
        else:
            connection_pools[redis_url].append(client)
        return client

    def _get_pubsub_connection(self):
        return self._connection.pubsub()

    def _connect(self, redis_url: str) -> StrictRedis:
        _, client = rsu_connect(redis_url)
        if (client is None):
            raise ConnectionError("Could not connect to redis")
        # return Redis.from_url(redis_url)
        return client  # type: ignore

    async def close(self) -> None:
        return self._connection.close()

    async def set(self, name: str, obj: Any) -> bool:
        name = self.prefixed(name)
        result = self._connection.set(name, obj)
        if result is not None:
            return True
        return False

    async def get(self, name: str) -> Optional[Any]:
        name = self.prefixed(name)
        return self._connection.get(name)

    async def lpush(self, name: str, obj) -> int:
        name = self.prefixed(name)
        return self._connection.lpush(name, obj)

    async def rpush(self, name: str, obj) -> int:
        name = self.prefixed(name)
        return self._connection.rpush(name, obj)

    async def lpop(self, name: str) -> Optional[str]:
        name = self.prefixed(name)
        return self._connection.lpop(name)

    async def lrem(self, name: str, obj) -> int:
        name = self.prefixed(name)
        return self._connection.lrem(name, 1, obj)

    async def lindex_rem(self, name: str, index: int) -> int:
        name = self.prefixed(name)
        future1 = self.lset(name, index, "DELETED")
        future2 = self.lrem(name, "DELETED")
        result1 = ensure_future(future1, loop=self.loop)
        result2 = ensure_future(future2, loop=self.loop)
        await wait([result1])
        await wait([result2])
        return result2.result()

    async def lindex_obj(self, name: str, index: int, json_model: Any) -> Any:
        name = self.prefixed(name)
        future = self.lindex(name, index)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        redis_str = result.result()
        if redis_str is not None:
            return json_model.parse_raw(redis_str)
        return json_model.parse_raw("{}")

    async def lindex(self, name: str, index: int) -> Optional[str]:
        name = self.prefixed(name)
        return self._connection.lindex(name, index)

    async def llen(self, name: str) -> int:
        name = self.prefixed(name)
        return self._connection.llen(name)

    async def lset(self, name: str, index: int, obj: Any) -> bool:
        name = self.prefixed(name)
        return self._connection.lset(name, index, obj)

    async def subscribe(self, channel: str):
        return self._pubsub_connection.subscribe(channel)

    async def unsubscribe(self, channel: str):
        return self._pubsub_connection.unsubscribe(channel)

    async def get_message(self) -> Optional[Dict[str, Any]]:
        try:
            # mutex, so that only one thread can read at a time
            # self.mutex.acquire()
            # get_message() returns None if there are no messages
            return self._pubsub_connection.get_message(
                ignore_subscribe_messages=True
            )
        except ConnectionError:
            return None
        finally:
            pass
            # release the mutex, so that another thread can read
            # self.mutex.release()

    async def publish(self, channel: str, obj) -> int:
        channel = self.prefixed(channel)
        return self._connection.publish(channel, obj)
