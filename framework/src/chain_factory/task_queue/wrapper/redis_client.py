from asyncio import AbstractEventLoop, ensure_future, wait
from logging import debug
from aioredis.client import PubSub, Redis
from aioredis.exceptions import ConnectionError
# from aioredis.exceptions import TimeoutError
from threading import Lock
from typing import Dict, Any, List
# from ..decorators.repeat import repeat
# from ..decorators.repeat import repeat_async

connection_pools: Dict[str, List[Redis]] = {}


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
        self._connection: Redis = self._get_connection(
            redis_url=redis_url,
        )
        self._key_prefix = key_prefix
        self._pubsub_connection: PubSub = self._get_pubsub_connection()
        self.mutex = Lock()

    @property
    def key_prefix(self):
        return self._key_prefix

    def prefixed(self, key):
        return f"{self.key_prefix}_{key}"

    def _get_connection(
        self,
        redis_url: str,
    ):
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

    def _connect(
        self,
        redis_url: str,
    ) -> Redis:
        return Redis.from_url(redis_url)

    async def close(self):
        future = self._connection.close()
        result = ensure_future(future, loop=self.loop)
        try:
            await wait([result])
            return result.result()
        except ValueError:
            return None

    async def set(self, name: str, obj):
        name = self.prefixed(name)
        future = self._connection.set(name, obj)
        result = ensure_future(future, loop=self.loop)
        try:
            await wait([result])
            return result.result()
        except ValueError:
            return None

    async def get(self, name: str):
        name = self.prefixed(name)
        future = self._connection.get(name)
        result = ensure_future(future, loop=self.loop)
        try:
            await wait([result])
            result1 = result.result()
            return result1
        except ValueError:
            return None

    async def lpush(self, name: str, obj):
        name = self.prefixed(name)
        future = self._connection.lpush(name, obj)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def rpush(self, name: str, obj):
        name = self.prefixed(name)
        future = self._connection.rpush(name, obj)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def lpop(self, name: str):
        name = self.prefixed(name)
        future = self._connection.lpop(name)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def lrem(self, name: str, obj):
        name = self.prefixed(name)
        future = self._connection.lrem(name, 1, obj)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def lindex_rem(self, name: str, index: int):
        name = self.prefixed(name)
        future1 = self.lset(name, index, "DELETED")
        future2 = self.lrem(name, "DELETED")
        result1 = ensure_future(future1, loop=self.loop)
        result2 = ensure_future(future2, loop=self.loop)
        await wait([result1])
        await wait([result2])
        return result2.result()

    async def lindex_obj(self, name: str, index: int, json_model: Any):
        name = self.prefixed(name)
        future = self.lindex(name, index)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        redis_bytes = result.result()
        if redis_bytes is not None:
            redis_decoded = redis_bytes.decode("utf-8")
            return json_model.parse_raw(redis_decoded)
        return json_model.parse_raw("{}")

    async def lindex(self, name: str, index: int) -> bytes:
        name = self.prefixed(name)
        future = self._connection.lindex(name, index)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def llen(self, name: str):
        name = self.prefixed(name)
        future = self._connection.llen(name)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def lset(self, name: str, index: int, obj):
        name = self.prefixed(name)
        future = self._connection.lset(name, index, obj)
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def subscribe(self, channel: str):
        future = self._pubsub_connection.subscribe(channel)
        return await future

    async def listen(self):
        future = self._pubsub_connection.listen()
        result = ensure_future(future, loop=self.loop)
        await wait([result])
        return result.result()

    async def get_message(self):
        try:
            self.mutex.acquire()
            future = self._pubsub_connection.get_message(
                ignore_subscribe_messages=True)
            return await future
        except ConnectionError:
            return None
        finally:
            self.mutex.release()

    async def publish(self, channel: str, obj):
        channel = self.prefixed(channel)
        return self._connection.publish(channel, obj)
