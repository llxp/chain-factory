from aioredis import Redis
from bson.regex import Regex
from fastapi import APIRouter, Depends
from typing import Optional, List

from odmantic import AIOEngine

from framework.src.chain_factory.task_queue.models.\
    mongodb_models import RegisteredTask
from ...auth.depends import CheckScope
from .utils import (
    default_namespace, get_odm_session, get_redis_client, node_active,
    unwind, match, project, skip_stage, limit_stage
)


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.get("/active_tasks", dependencies=[user_role])
async def active_tasks(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    # time.sleep(0.5)
    active_nodes = await nodes(namespace, database, redis_client)
    tasks_result = await tasks(
        namespace,
        search,
        database,
        page,
        page_size,
        active_nodes if active_nodes else None,
    )
    return tasks_result


async def nodes(namespace: str, database: AIOEngine, redis_client: Redis):
    node_list: List[str] = []

    def match_namespace():
        query = {}
        if not default_namespace(namespace):
            return (RegisteredTask.namespace == namespace)
        return query

    node_name_list = database.find(RegisteredTask, (
        (match_namespace())
    ))
    async for node_name in node_name_list:
        if (
            await node_active(
                node_name["node_name"],
                node_name["namespace"],
                redis_client
            )
        ):
            node_list.append(node_name)
    return node_list


async def tasks(
    namespace: str,
    search: str,
    database: AIOEngine,
    page: int = None,
    page_size: int = None,
    nodes=[],
):
    unwind_stage = unwind("$tasks")

    def match_stage():
        stage = match({})
        if search:
            rgx = Regex("^{}".format(search))
            stage["$match"] = {"tasks.name": {"$regex": rgx}}
        if not default_namespace(namespace):
            stage["$match"]["namespace"] = namespace
        if nodes or nodes is None:
            stage["$match"]["node_name"] = {
                "$in": [node["node_name"] for node in (nodes if nodes else [])]
            }
            stage["$match"]["namespace"] = {
                "$in": [node["namespace"] for node in (nodes if nodes else [])]
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
    collection = database.get_collection(RegisteredTask)
    result = await collection.aggregate(aggregate_query)
    return (
        result[0]
        if len(result) > 0
        else {"node_tasks": [], "total_count": 0}
    )
