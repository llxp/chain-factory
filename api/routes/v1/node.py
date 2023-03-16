from typing import List
from logging import info

# fastapi
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

# redis, odmantic, motor
from redis import Redis
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorCollection

# models from chain_factory framework
from framework.src.chain_factory.models.redis_models import TaskControlMessage  # noqa: E501

# data types
from .models.namespace import Namespace

# utils
from .utils import get_odm_session
from .utils import get_redis_client
from .utils import node_active
from .utils import get_allowed_namespaces
from .utils import get_username
from .utils import default_namespace

# auth
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
    # TODO: review this function, if it is needed
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
        active = node_active(
            node_name=node_tasks['node_name'],
            namespace=node_tasks_namespace,
            domain=namespace_objs[0].domain,
            redis_client=redis_client
        )
        if namespace_objs and active:
            nodes.append(node_tasks['node_name'])  # noqa: E501
    redis_keys = [
        namespace.namespace + '_' + 'node_control_channel'
        for namespace in namespaces
    ]
    for redis_key in redis_keys:
        redis_client.publish(
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
    # create dictionary: {namespace: node_tasks}
    registered_tasks_result = {
        ns: doc  # key: namespace, value: node_tasks
        for ns, collection in collections.items()  # iterate over all collections: key: ns (namespace), value: collection (node_tasks)
        async for doc in collection.find()  # retrieve all documents from collection
        if (ns == namespace or default_namespace(namespace))  # check, if default namespace or specific namespace
    }
    nodes = list()
    for ns, task in registered_tasks_result.items():
        node_name = task['node_name']
        if node_name:
            namespace_obj = await Namespace.get(database, ns, username)  # noqa: E501
            if namespace_obj:
                info(f"Found namespace {namespace_obj.namespace}")
                domain = namespace_obj.domain
                nodes.append({
                    "node_name": node_name,
                    "namespace": ns,
                    "active": await node_active(node_name, ns, domain, redis_client)  # noqa: E501
                })
    info(f"Found nodes {nodes}")
    return nodes


@api.delete('/{node_name}', dependencies=[node_admin_role])
async def delete_node(
    node_name: str,
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[Namespace] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    """Delete a node from the database.
    If there are multiple nodes with the same name,
    the first found node will be deleted.
    If there are no nodes with the name, this will fail.

    Raises:
        HTTPException: Raises exception if multiple nodes were found
        HTTPException: Raises exception if node was not found
        HTTPException: Raises exception if namespace not found or access denied

    Returns:
        Str: Node deleted
    """    
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
            raise HTTPException(status_code=500, detail="Multiple nodes found with the same name")  # noqa: E501
        raise HTTPException(status_code=404, detail="Node not found")
    raise HTTPException(status_code=401, detail=f"Namespace {namespace} not found or not allowed")  # noqa: E501
