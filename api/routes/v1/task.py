from aioredis import Redis
from bson.regex import Regex
from fastapi import APIRouter, Depends
from typing import Optional, List

from odmantic import AIOEngine
from api.auth.utils.credentials import get_domain

from framework.src.chain_factory.task_queue.models.\
    mongodb_models import NodeTasks
from ...auth.depends import CheckScope, get_username
from .utils import (
    default_namespace, get_odm_session, get_redis_client, node_active,
    unwind, match, project, skip_stage, limit_stage
)
from .models.namespace import Namespace


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.get("/active_tasks", dependencies=[user_role])
async def active_tasks(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    username: str = Depends(get_username),
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    # time.sleep(0.5)
    active_nodes = await nodes(namespace, username, database, redis_client)
    tasks_result = await tasks(
        namespace,
        username,
        search,
        database,
        page,
        page_size,
        active_nodes,
    )
    return tasks_result


async def nodes(
    namespace: str,
    username: str,
    database: AIOEngine,
    redis_client: Redis
) -> List[NodeTasks]:
    node_list: List[NodeTasks] = []
    domain = await get_domain(username)
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501
    node_tasks_collections = [namespace_db.get_collection(NodeTasks.__collection__) for namespace_db in namespace_dbs]  # noqa: E501

    def match_namespace():
        query = {}
        if not default_namespace(namespace):
            return (NodeTasks.namespace == namespace)
        return query

    node_name_lists = [node_tasks_collection.find(
        (match_namespace())
    ) for node_tasks_collection in node_tasks_collections]

    for node_name_list in node_name_lists:
        async for node_name in node_name_list:
            node: NodeTasks = NodeTasks(**node_name)
            if (
                await node_active(
                    node.node_name,
                    node.namespace,
                    domain,
                    redis_client
                )
            ):
                node_list.append(node)
    return node_list


async def tasks(
    namespace: str,
    username: str,
    search: str,
    database: AIOEngine,
    page: int = None,
    page_size: int = None,
    nodes: List[NodeTasks] = [],
):
    unwind_stage = unwind("$tasks")

    def match_stage():
        stage = match({})
        if search:
            rgx = Regex("^{}".format(search))
            stage["$match"] = {"tasks.name": {"$regex": rgx}}
        if not default_namespace(namespace):
            stage["$match"]["namespace"] = namespace
        if nodes is not None:
            stage["$match"]["node_name"] = {
                "$in": [
                    node.node_name for node in (
                        nodes if nodes is not None else []
                    )
                ]
            }
            stage["$match"]["namespace"] = {
                "$in": [
                    node.namespace for node in (
                        nodes if nodes is not None else []
                    )
                ]
            }
        return stage

    aggregate_query = [
        stage
        for stage in [
            match_stage(),
            unwind_stage,
            match_stage(),
            project({"_id": 0}),
            {
                "$facet": {
                    "node_tasks": [
                        stage2
                        for stage2 in [
                            skip_stage(page, page_size),
                            limit_stage(page, page_size)
                        ]
                        if stage2 != {}
                    ],
                    "total_count": [{"$count": "count"}],
                }
            },
            project({
                "node_tasks": 1,
                "total_count": {"$first": "$total_count.count"},
            }),
        ]
        if stage != {}
    ]
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(
        database, username, namespace)
    if namespace_dbs:
        collections = [namespace_db.get_collection(NodeTasks.__collection__) for namespace_db in namespace_dbs]  # noqa: E501
        result_cursors = [collection.aggregate(aggregate_query) for collection in collections]  # noqa: E501
        results = [await result_cursor.to_list(1) for result_cursor in result_cursors]  # noqa: E501
        results_0 = [r for result in results for r in result]
        result = {
            "node_tasks": [r for result in results_0 for r in result["node_tasks"]],  # noqa: E501
            "total_count": sum([result["total_count"] for result in results_0 if "total_count" in result and result["total_count"] is not None]),  # noqa: E501
        }
    else:
        result = {"node_tasks": [], "total_count": 0}
    return result
