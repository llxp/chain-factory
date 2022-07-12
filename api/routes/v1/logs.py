from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorCollection
from collections import ChainMap

from ...auth.depends import CheckScope, get_username
from .utils import (
    get_odm_session,
    facet, match, project, limit_stage, skip_stage, lookup_logs,
    get_allowed_namespaces,
)
from .models.namespace import Namespace


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))
cleanup_scope = Depends(CheckScope(scope='cleanup'))


@api.get('/task_logs', dependencies=[user_role])
async def task_log(
    task_id: str,
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_dbs = await Namespace.get_namespace_dbs(
        database, username)
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("logs") for db in namespace_dbs
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
                '$first': '$total_count.count'
            }
        })
    ]
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    return aggregations[0]


@api.get('/workflow_logs', dependencies=[user_role])
async def workflow_logs(
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_namespace_dbs(
        database, username)
    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("task_workflow_association") for db in namespace_dbs
    ]
    pipeline = [
        lookup_logs('task.task_id', 'logs'),
        project({
            '_id': 0,
            'logs._id': 0,
            'logs.task_id': 0,
            'task.name': 0,
            'task.arguments': 0
        }),
        match({'workflow_id': workflow_id}),
        project({
            'task_id': '$task.task_id',
            'logs': '$logs.log_line'
        }),
        {
            "$facet": {
                "task_logs": [
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
            'task_logs': 1,
            'total_count': {
                '$first': '$total_count.count'
            }
        }),
    ]
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    results = dict(ChainMap(*aggregations))
    return results


@api.delete('/workflow_logs', dependencies=[cleanup_scope])
async def delete_workflow_logs(
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    # 1. get all task_ids for this workflow
    # 2. delete all logs for those tasks
    namespace_dbs = await Namespace.get_namespace_dbs(
        database, username)
    if namespace_dbs:
        collections: List[AsyncIOMotorCollection] = [
            db.get_collection("task_workflow_association") for db in namespace_dbs  # noqa: E501
        ]
        cursors = [
            collection.find({'workflow_id': workflow_id}) for collection in collections  # noqa: E501
        ]
        tasks_results = [
            await collection.to_list(None) for collection in cursors
        ]
        task_ids = [
            task['task']['task_id'] for task in tasks_results[0]
        ]
        logs_collections = [
            db.get_collection("logs") for db in namespace_dbs
        ]
        task_status_collections = [
            db.get_collection("task_status") for db in namespace_dbs
        ]
        workflow_collections = [
            db.get_collection("workflow") for db in namespace_dbs
        ]
        workflow_existing = await workflow_collections[0].find_one(
            {'workflow_id': workflow_id})
        if not workflow_existing:
            raise HTTPException(
                status_code=501,
                detail="Workflow not found"
            )
        for workflow_collection in workflow_collections:
            await workflow_collection.delete_many({'workflow_id': workflow_id})
        for collection in collections:
            await collection.delete_many({
                'workflow_id': workflow_id
            })
        for logs_collection in logs_collections:
            await logs_collection.delete_many({
                'task_id': {'$in': task_ids}
            })
        for task_status_collection in task_status_collections:
            await task_status_collection.delete_many({
                'task_id': {'$in': task_ids}
            })
        return {'message': 'logs deleted'}
    raise HTTPException(
        status_code=501,
        detail='you are not allowed to delete logs of this workflow'
    )
