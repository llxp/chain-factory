from aioredis import Redis
from bson.regex import Regex
from fastapi import APIRouter, Depends
from typing import Optional, List, Dict
from logging import getLogger

from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorCollection

from framework.src.chain_factory.task_queue.models.\
    mongodb_models import NodeTasks
from ...auth.depends import CheckScope, get_username
from .utils import (
    add_fields, facet, get_allowed_namespaces,
    get_odm_session, get_redis_client, node_active,
    unwind, match, project, skip_stage, limit_stage
)
from .models.namespace import Namespace

LOGGER = getLogger(__name__)

api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.get("/active", dependencies=[user_role])
async def active_tasks(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    username: str = Depends(get_username),
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    active_nodes = await nodes(namespace, username, database, redis_client)
    LOGGER.debug(active_nodes)
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
    namespace_entries = await Namespace.get_multiple(database, username)
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501
    node_tasks_collections: Dict[str, AsyncIOMotorCollection] = {ns: namespace_db.get_collection(NodeTasks.__collection__) for ns, namespace_db in namespace_dbs.items()}  # noqa: E501

    node_name_lists: list = {
        ns: node_tasks_collection.find()
        for ns, node_tasks_collection in node_tasks_collections.items()
    }

    for ns, node_name_list in node_name_lists.items():
        async for node_name in node_name_list:
            node_obj: NodeTasks = NodeTasks(**node_name)
            for namespace_entry in namespace_entries:
                domain = namespace_entry.domain
                if (
                    await node_active(
                        node_obj.node_name,
                        ns,
                        domain,
                        redis_client
                    )
                ):
                    node_obj.namespace = ns
                    node_list.append(node_obj)
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
        # if not default_namespace(namespace):
        #     stage["$match"]["namespace"] = namespace
        if nodes is not None:
            stage["$match"]["node_name"] = {
                "$in": [
                    node.node_name for node in (
                        nodes if nodes is not None else []
                    )
                ]
            }
            # stage["$match"]["namespace"] = {
            #     "$in": [
            #         node.namespace for node in (
            #             nodes if nodes is not None else []
            #         )
            #     ]
            # }
        return stage

    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501
    if namespace_dbs:
        aggregate_query = {
            ns: [
                stage
                for stage in [
                    match_stage(),
                    unwind_stage,
                    match_stage(),
                    add_fields({"namespace": ns}),
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
                        "total_count": {"$arrayElemAt": ["$total_count.count", 0]},  # noqa: E501
                    }),
                ]
                if stage != {}
            ]
            for ns, db in namespace_dbs.items()
        }
        LOGGER.debug(aggregate_query)
        collections = {ns: namespace_db.get_collection(NodeTasks.__collection__) for ns, namespace_db in namespace_dbs.items()}  # noqa: E501
        result_cursors = [collection.aggregate(aggregate_query[ns]) for ns, collection in collections.items()]  # noqa: E501
        results = [await result_cursor.to_list(1) for result_cursor in result_cursors]  # noqa: E501
        results_0 = [r for result in results for r in result]
        result = {
            "node_tasks": [r for result in results_0 for r in result["node_tasks"]],  # noqa: E501
            "total_count": sum([result["total_count"] for result in results_0 if "total_count" in result and result["total_count"] is not None]),  # noqa: E501
        }
    else:
        result = {"node_tasks": [], "total_count": 0}
    return result


@api.get('/{task_id}/logs', dependencies=[user_role])
async def task_logs(
    task_id: str,
    namespace: str,
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("logs") for ns, db in namespace_dbs.items()
    ]
    pipeline = [
        match({'task_id': task_id}),
        project({
            'log_line': 1,
            '_id': 0,
        }),
        facet({
            "log_lines": [
                stage2
                for stage2 in [
                    skip_stage(page, page_size),
                    limit_stage(page, page_size)
                ]
                if stage2 != {}
            ],
            "total_count": [{"$count": "count"}],
        }),
        project({
            'log_lines': '$log_lines.log_line',
            'total_count': {
                '$arrayElemAt': ['$total_count.count', 0]
            }
        })
    ]
    LOGGER.debug(pipeline)
    LOGGER.debug(collections)
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    return aggregations[0]
