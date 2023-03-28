from _thread import interrupt_main
from datetime import datetime
from asyncio import sleep
from asyncio import AbstractEventLoop

# direct imports
from .client_pool import ClientPool

# models
from .models.redis_models import Heartbeat

# wrapper
from .wrapper.redis_client import RedisClient

# settings
from .common.settings import heartbeat_redis_key
from .common.settings import heartbeat_sleep_time


class ClusterHeartbeat():
    def __init__(
        self,
        namespace: str,
        node_name: str,
        client_pool: ClientPool,
        loop: AbstractEventLoop
    ):
        self._client_pool = client_pool
        self.node_name = node_name
        self.namespace = namespace
        self.heartbeat_running = False
        self.loop = loop
        self.task = None

    def start_heartbeat(self):
        """
        starts the heartbeat thread
        """
        self.heartbeat_running = True
        self._heartbeat_thread()

    def stop_heartbeat(self):
        """
        stops the heartbeat thread
        """
        if self.heartbeat_running:
            self.heartbeat_running = False
            if self.task:
                self.task.cancel()

    def _current_timestamp(self):
        return datetime.utcnow()

    def _redis_key(self):
        return heartbeat_redis_key + "_" + self.node_name

    def _json_heartbeat(self):
        heartbeat = Heartbeat(
            node_name=self.node_name,
            namespace=self.namespace,
            last_time_seen=self._current_timestamp()
        )
        return heartbeat.json()

    async def _set_heartbeat(self, redis_client: RedisClient):
        result = await redis_client.set(
            self._redis_key(),
            self._json_heartbeat()
        )
        if not result:
            # interrupt the main thread, if the heartbeat fails
            # so that the node can be cleanly shutdown and restarted
            interrupt_main()

    def _heartbeat_thread(self):
        """
        updates a key in redis to show the current uptime of the node
        and waits a specified amount of time
        repeats as long as the node is running
        """
        self.task = self.loop.create_task(self._run_loop())

    async def _run_loop(self):
        redis_client = await self._client_pool.redis_client()
        while self.heartbeat_running:
            await self._set_heartbeat(redis_client)
            await sleep(heartbeat_sleep_time)
