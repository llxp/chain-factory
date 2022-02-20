from aioredis import Redis
from fastapi import APIRouter, Depends
from odmantic import AIOEngine

from framework.src.chain_factory.task_queue.models.\
    mongodb_models import RegisteredTask
from framework.src.chain_factory.task_queue.models.redis_models import (
    TaskControlMessage,
)
from .utils import (
    default_namespace, get_odm_session, get_redis_client, node_active
)
from ...auth.depends import CheckScope


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))
node_admin_role = Depends(CheckScope(scope='node_admin'))


@ api.post('/stop_node', dependencies=[node_admin_role])
def stop_node(
    namespace: str,
    node_name: str,
    redis_client: Redis = Depends(get_redis_client)
):
    redis_client.publish(
        namespace + '_' + 'node_control_channel',
        TaskControlMessage(
            workflow_id=node_name,
            command='stop'
        ).json())
    return 'OK'


@ api.get('/node_metrics', dependencies=[user_role])
async def node_metrics(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client)
):
    if default_namespace(namespace):
        registered_tasks_result = await database.find(RegisteredTask, {})
    else:
        registered_tasks_result = await database.find(
            RegisteredTask, RegisteredTask.namespace == namespace)
    nodes = dict()
    async for task in registered_tasks_result:
        node_name = task['node_name']
        node_namespace = task['namespace']
        if node_name:
            node_status = await node_active(
                node_name, node_namespace, redis_client)
            nodes[node_name] = node_status
    return nodes
