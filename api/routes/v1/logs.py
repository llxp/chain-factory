from typing import Optional
from fastapi import APIRouter, Depends
from odmantic import AIOEngine

from framework.src.chain_factory.task_queue.models.\
    mongodb_models import Task, TaskLog
from ...auth.depends import CheckScope
from .utils import (
    get_odm_session,
    facet, match, project, limit_stage, skip_stage, lookup_logs
)


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.get('/task_logs', dependencies=[user_role])
async def task_log(
    task_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    database: AIOEngine = Depends(get_odm_session),
):
    collection = database.get_collection(TaskLog)
    log_result = await collection.aggregate([
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
    ])
    return (await log_result.to_list(1))[0]


@api.get('/workflow_logs', dependencies=[user_role])
async def workflow_logs(
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    collection = database.get_collection(Task)
    log_result = await collection.aggregate([
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
    ])
    return (await log_result.to_list(1))[0]
