from aioredis import Redis
from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection

from framework.src.chain_factory.task_queue.models.redis_models import (
    TaskControlMessage,
)
from .models.namespace import Namespace
from .utils import (
    get_odm_session, get_redis_client, node_active,
    get_allowed_namespaces, get_username, default_namespace
)
from ...auth.depends import CheckScope
from ...auth.utils.credentials import get_domain


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))
node_admin_role = Depends(CheckScope(scope='node_admin'))


@ api.post('/stop_node', dependencies=[node_admin_role])
async def stop_node(
    namespace: str,
    node_name: str,
    redis_client: Redis = Depends(get_redis_client),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    namespaces: List[str] = Depends(get_allowed_namespaces),
):
    get_namespace_dbs = await Namespace.get_namespace_dbs(
        database, username)
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("node_tasks") for db in get_namespace_dbs
    ]
    find_query = {'namespace': namespace} \
        if not default_namespace(namespace) else {}
    registered_tasks_result = [
        doc for collection in collections
        async for doc in collection.find(find_query)
    ]
    domain = await get_domain(username)
    nodes = [
        task['node_name']
        for task in registered_tasks_result
        if await node_active(
            task['node_name'],
            task['namespace'],
            domain,
            redis_client
        )
    ]
    redis_keys = [
        namespace.namespace + '_' + 'node_control_channel'
        for namespace in namespaces
    ]
    for redis_key in redis_keys:
        await redis_client.publish(
            redis_key,
            TaskControlMessage(
                workflow_id=node_name,
                command='stop'
            ).json())
    return nodes


@ api.get('/node_metrics', dependencies=[user_role])
async def node_metrics(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_namespace_dbs(
        database, username)
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("node_tasks") for db in namespace_dbs
    ]
    find_query = {'namespace': namespace} \
        if not default_namespace(namespace) else {}
    registered_tasks_result = [
        doc for collection in collections
        async for doc in collection.find(find_query)
    ]
    nodes = dict()
    for task in registered_tasks_result:
        node_name = task['node_name']
        node_namespace = task['namespace']
        if node_name:
            domain = await get_domain(username)
            node_status = await node_active(
                node_name, node_namespace, domain, redis_client)
            nodes[node_name] = node_status
    return nodes
