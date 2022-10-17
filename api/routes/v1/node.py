from logging import info
from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException
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


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))
node_admin_role = Depends(CheckScope(scope='node_admin'))


@ api.post('/{node_name}/stop', dependencies=[node_admin_role])
async def stop_node(
    namespace: str,
    node_name: str,
    redis_client: Redis = Depends(get_redis_client),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    namespaces: List[Namespace] = Depends(get_allowed_namespaces),
):
    namespace_dbs = await Namespace.get_namespace_dbs(database, username)
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("node_tasks") for ns, db in namespace_dbs.items()
    ]
    find_nodes_query = {'namespace': namespace} if not default_namespace(namespace) else {}  # noqa: E501
    registered_node_tasks_result = [
        doc for collection in collections
        async for doc in collection.find(find_nodes_query)
    ]
    nodes = []
    for node_tasks in registered_node_tasks_result:
        node_tasks_namespace = node_tasks['namespace']
        namespace_objs = [ns for ns in namespaces if ns.namespace == node_tasks_namespace]  # noqa: E501
        active = node_active(node_tasks['node_name'], node_tasks_namespace, namespace_objs[0])  # noqa: E501
        if namespace_objs and active:
            nodes.append(node_tasks['node_name'])  # noqa: E501
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


@ api.get('/metrics', dependencies=[user_role])
async def node_metrics(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_namespace_dbs(database, username)
    collections = {
        ns: db.get_collection("node_tasks") for ns, db in namespace_dbs.items()
    }
    registered_tasks_result = {
        ns: doc for ns, collection in collections.items()
        async for doc in collection.find()
        if (ns == namespace or default_namespace(namespace))
    }
    nodes = dict()
    for ns, task in registered_tasks_result.items():
        node_name = task['node_name']
        if node_name:
            namespace_obj = await Namespace.get(database, ns, username)  # noqa: E501
            if namespace_obj:
                info(f"Found namespace {namespace_obj.namespace}")
                domain = namespace_obj.domain
                node_status = await node_active(
                    node_name, ns, domain, redis_client)
                nodes[node_name] = node_status
    return nodes


@api.delete('/{node_name}', dependencies=[node_admin_role])
async def delete_node(
    node_name: str,
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[Namespace] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    namespace_db = await Namespace.get_namespace_db(database, namespace, username, False)  # noqa: E501
    if namespace_db is not None:
        node_tasks_collection = await namespace_db.get_collection("node_tasks")
        delete_node_query = {'node_name': node_name}
        deletion_result = await node_tasks_collection.delete_one(delete_node_query)  # noqa: E501
        info(deletion_result.raw_result)
        info(deletion_result.deleted_count)
        if deletion_result.deleted_count == 1:
            return "Node deleted"
        if deletion_result.deleted_count > 1:
            raise HTTPException(
                status_code=500,
                detail="Multiple nodes found with the same name")
        raise HTTPException(status_code=404, detail="Node not found")
    raise HTTPException(status_code=401, detail=f"Namespace {namespace} not found or not allowed")  # noqa: E501
