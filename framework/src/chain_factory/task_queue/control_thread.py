from .wrapper.interruptable_thread import (
  InterruptableThread, ThreadAbortException
)
from .models.redis_models import TaskControlMessage
from .wrapper.redis_client import RedisClient
from typing import Dict, Callable, Union
from logging import info, exception, debug
from asyncio import run as run_asyncio
from time import sleep
from traceback import print_exc
from sys import stdout


class ControlThread(InterruptableThread):
    def __init__(
        self,
        workflow_id: str,
        control_actions: Dict[str, Callable],
        redis_client: RedisClient,
        control_channel: str,
        thread_name: str = ""
    ):
        InterruptableThread.__init__(self)
        self.workflow_id = workflow_id
        self.control_actions = control_actions
        self.redis_client = redis_client
        self.control_channel = control_channel
        self.run_thread = True
        self.thread_name = thread_name
        debug(self.control_channel)

    def stop(self):
        self.run_thread = False

    def run(self):
        run_asyncio(self.run_async())

    async def run_async(self):
        try:
            debug(self.control_channel)
            await self.redis_client.subscribe(self.control_channel)
            while self.run_thread:
                msg = await self.redis_client.get_message()
                if msg is not None:
                    info(msg)
                    if await self._control_task_thread_handle_channel(msg):
                        break
                sleep(0.1)
            await self.redis_client._pubsub_connection.unsubscribe(
                self.control_channel)
        except ThreadAbortException:
            return

    async def _control_task_thread_handle_channel(self, msg: Union[None, Dict]):  # noqa: E501
        try:
            if await self._control_task_thread_handle_data(msg):
                return True
        except Exception as e:
            exception(e)
            print_exc(file=stdout)
            return True
        return False

    async def _control_task_thread_handle_data(
        self,
        msg: Union[None, Dict]
    ):
        data: bytes = msg["data"]
        if type(data) == bytes:
            decoded_data = data.decode("utf-8")
            parsed_data = TaskControlMessage.parse_raw(decoded_data)
            debug(parsed_data)
            if parsed_data.workflow_id == self.workflow_id:
                for command in self.control_actions:
                    if parsed_data.command == command:
                        debug(f"executing command: {command}")
                        self.control_actions[command]()
                        return True
        return False
