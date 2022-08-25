from collections import ChainMap
from logging import info
from re import compile, UNICODE
from bson.regex import Regex
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorCollection

from ...auth.depends import CheckScope, get_username
from .utils import (
    begin_end_stage, check_namespace_allowed_even_disabled, get_allowed_namespaces, get_allowed_namespaces_even_disabled,  # noqa: E501
    get_odm_session, match, project, lookup,
    sort_stage, skip_stage, limit_stage,
    lookup_logs, default_namespace, lookup_workflow_status
)
from .models.namespace import Namespace


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))
cleanup_scope = Depends(CheckScope(scope='cleanup'))


@api.get('', dependencies=[user_role])
async def workflows(
    namespace: str,
    namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    begin: Optional[str] = None,
    end: Optional[str] = None,
):
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace, True)  # noqa: E501
    namespace_dbs = [db for db in namespace_dbs if db is not None]  # noqa: E501

    if not namespace_dbs or namespace_dbs is None:
        raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501

    def search_stage():
        stages = []
        stage = match({
            '$and': [
                {
                    "workflow.namespace": {
                        '$exists': 'true',
                        '$nin': ["", 'null']
                    },
                },
            ],
        })
        stage = begin_end_stage(begin, end, stage)
        if search:
            search_splitted = search.split(' ')
            patterns = []
            keys = []

            def get_regex(pattern):
                regex = compile(pattern)
                rgx = Regex.from_native(regex)
                rgx.flags ^= UNICODE
                return rgx

            operators = {
                'name': {'type': 'str', 'key': 'tasks.name'},
                'tags': {'type': 'list', 'key': 'tasks.tags'},
                'namespace': {'type': 'str', 'key': 'workflow.namespace'},
                'date': {'type': 'str', 'key': 'created_date'},
                'arguments': {'type': 'dict', 'key': 'tasks.arguments'},
                'logs': {'type': 'logs', 'key': 'logs.log_line'}
            }

            def get_operator(operator, value):
                operator_obj = operators[operator]
                if (
                    operator_obj['type'] == 'str' or
                    operator_obj['type'] == 'list'
                ):
                    return {
                        operator_obj['key']: {
                            '$regex': get_regex(value)
                        }
                    }, None
                elif operator_obj['type'] == 'dict':
                    splitted_map = value.split(':')
                    if len(splitted_map) >= 2:
                        joined_map = ''.join(splitted_map[1:])
                        splitted_map[1] = joined_map
                    if len(splitted_map) < 2:
                        return None, None
                    project_stage = {
                        '$addFields': {
                            '{}_string'.format(splitted_map[0]): {
                                "$map": {
                                    "input": "${}.{}".format(
                                        operator_obj['key'],
                                        splitted_map[0]
                                    ),
                                    "as": "row",
                                    "in": {
                                        "value": {"$toString": '$$row'}
                                    }
                                }
                            },
                        }
                    }
                    stages.append(project_stage)
                    return {
                        '{}_string.value'.format(splitted_map[0]): {
                            '$regex': get_regex(splitted_map[1])
                        }
                    }, '{}_string'.format(splitted_map[0])
                elif operator_obj['type'] == 'logs':
                    stages.append(
                        lookup_logs('tasks.task_id', 'logs')
                    )
                    return {
                        'logs.log_line': {
                            '$regex': get_regex(value)
                        }
                    }, 'logs'
                return None, None
            for search_pattern in search_splitted:
                if ':' in search_pattern:
                    tokens = search_pattern.split(':')
                    operator, value = tokens[0], ':'.join(tokens[1:])
                    if operator in operators:
                        pattern_temp, key = get_operator(operator, value)
                        if key:
                            keys.append(key)
                        if pattern_temp:
                            patterns.append(pattern_temp)
                else:
                    pattern_temp, key = get_operator('name', search_pattern)
                    if pattern_temp:
                        patterns.append(pattern_temp)
            if patterns:
                stage['$match']['$and'].append({
                    '$and': patterns
                })
        # if namespace and not default_namespace(namespace):
        #     stage['$match']['$and'].append({
        #         'workflow.namespace': namespace
        #     })
        stages.append(stage)
        if len(stages) >= 2:
            stages.append(project({key: 0 for key in keys}))
        return stages

    def check_empty(array: list):
        if array:
            return array
        return [
            skip_stage(0, 100),
            limit_stage(0, 100)
        ]

    pipeline = [
        stage for stage in [
            {
                '$group': {
                    '_id': {'workflow_id': '$workflow_id'},
                    'workflow': {
                        '$addToSet': {
                            'workflow_id': '$workflow_id',
                            'namespace': '$namespace',
                            'tags': '$tags',
                        },
                    },
                    'created_dates': {
                        '$push': '$created_date'
                    }
                }
            },
            lookup(
                'task_workflow_association',
                '_id.workflow_id',
                'workflow_id',
                'tasks'
            ),
            project({
                '_id': 0,
                'tasks._id': 0,
                'tasks.task.workflow_id': 0,
                'tasks.workflow_id': 0,
                'tasks.node_name': 0
            }),
            project({
                'tasks': '$tasks.task',
                'workflow': {
                    '$arrayElemAt': ['$workflow', 0]
                },
                'created_date': {
                    '$arrayElemAt': ['$created_dates', 0]
                }
            }),
            *search_stage(),
            project({
                'entry_task': {
                    '$arrayElemAt': ['$tasks', 0]
                },
                'workflow': 1,
                'created_date': 1,
            }),
            lookup_workflow_status('workflow.workflow_id', 'status'),
            project({
                'entry_task': 1,
                'workflow': 1,
                'created_date': 1,
                'status': {
                    '$ifNull': [
                        {'$arrayElemAt': ['$status.status', 0]},
                        'Running'
                    ]
                },
            }),
            project({'status._id': 0, 'entry_task.id': 0}),
            {
                "$facet": {
                    "workflows": check_empty([
                        stage2
                        for stage2 in [
                            sort_stage(sort_by, sort_order),
                            skip_stage(page, page_size),
                            limit_stage(page, page_size)
                        ]
                        if stage2 != {}
                    ]),
                    "total_count": [{"$count": "count"}],
                }
            },
            project({
                "workflows": 1,
                "total_count": {
                    '$ifNull': [{
                        "$arrayElemAt": ["$total_count.count", 0]
                    }, 0]
                },
                'count': {'$size': '$workflows'}
            })
        ] if stage != {}
    ]

    info('Pipeline: {}'.format(pipeline))
    info(namespace_dbs)
    info(f"Namespace DBs: {[db.name for db in namespace_dbs if db is not None]}")  # noqa: E501

    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("workflow") for db in namespace_dbs
    ]
    # workflow_tasks = collection.aggregate(pipeline)
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    print(aggregations)
    return aggregations[0]


@api.get(
    '/{workflow_id}/tasks',
    dependencies=[user_role, Depends(check_namespace_allowed_even_disabled)]
)
async def workflow_tasks(
    workflow_id: str,
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    pipeline = [
        project({'_id': 0}),
        match({'workflow_id': workflow_id}),
        project({'task.id': 0}),
        {
            "$facet": {
                "tasks": [
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
            'tasks': '$tasks.task',
            'total_count': {
                '$arrayElemAt': ['$total_count.count', 0]
            }
        })
    ]
    namespace_db = await Namespace.get_namespace_db(
        database, namespace, username)
    collection = namespace_db.get_collection("task_workflow_association")
    log_result = await collection.aggregate(pipeline).to_list(1)
    return log_result[0]


@api.get('/status', dependencies=[user_role])
async def workflow_status(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
    workflow_id: List[str] = Query([]),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501

    def match_stage():
        stage = match({})
        if isinstance(workflow_id, str):
            stage["$match"]['workflow_id'] = workflow_id
        elif isinstance(workflow_id, list) and len(workflow_id) > 0:
            stage["$match"]['workflow_id'] = {
                '$in': workflow_id
            }
        return stage

    collections = [
        db.get_collection("workflow_status")
        for db in namespace_dbs
    ]
    pipeline = [
        match_stage(),
        lookup_workflow_status('workflow_id', 'workflow_status'),
        project({
            'status': {
                '$ifNull': [
                    {
                        '$arrayElemAt': ["$workflow_status.status", 0]
                    },
                    'Running'
                ]
            },
            'workflow_id': 1,
            'workflow_status': 1,
            '_id': 0
        }),
        lookup('task_workflow_association', 'workflow_id', 'workflow_id', 'tasks'),  # noqa: E501
        project({
            'status': '$status',
            'workflow_id': 1,
            'tasks.task.task_id': 1,
        }),
        lookup('task_status', 'tasks.task.task_id', 'task_id', 'task_status1'),
        {
            "$addFields": {
                "tasks": {
                    "$map": {
                        "input": "$tasks",
                        "as": "row",
                        "in": {
                            '$mergeObjects': [
                                "$$row",
                                {
                                    '$arrayElemAt': [{
                                        '$filter': {
                                            'input': "$task_status1",
                                            'cond': {
                                                '$eq': [
                                                    "$$this.task_id",
                                                    "$$row.task.task_id"
                                                ]
                                            }
                                        }
                                    }, 0]
                                }
                            ]
                        }
                    }
                }
            }
        },
        project({
            'status': 1,
            'workflow_id': 1,
            'tasks': {
                "$map": {
                    "input": "$tasks",
                    "as": "row",
                    "in": {
                        "task_id": '$$row.task.task_id',
                        "status": {'$ifNull': ["$$row.status", 'Running']}
                    }
                }
            }
        })
    ]
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    return aggregations


@api.get('/metrics', dependencies=[user_role])
async def workflow_metrics(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[str] = Depends(get_allowed_namespaces_even_disabled),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501
    collections = [db.get_collection("workflow") for db in namespace_dbs]

    def match_stage():
        stage = match({})
        if not default_namespace(namespace):
            stage['$match']['namespace'] = namespace
        return stage
    pipeline = [
        match_stage(),
        lookup_workflow_status('workflow_id', 'workflow_status'),
        project({
            'status': {
                '$ifNull': [
                    {
                        '$arrayElemAt': ["$workflow_status.status", 0]
                    },
                    'Running'
                ]
            },
            'workflow_id': 1,
            'created_date': {
                '$ifNull': [
                    {
                        '$toString': {
                            '$arrayElemAt': ["$workflow_status.created_date", 0]  # noqa: E501
                        },
                    },
                    {
                        '$toString': "$created_date"
                    }
                ]
            },
            'namespace': 1,
        }),
        project({
            '_id': 0,
            'workflow_status._id': 0
        })
    ]
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    # results = dict(ChainMap(*aggregations))
    results = aggregations
    return results


@api.delete('/{workflow_id}/logs', dependencies=[cleanup_scope])
async def delete_workflow_logs(
    workflow_id: str,
    force: bool = Query(False),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    # 1. get all task_ids for this workflow
    # 2. delete all logs for those tasks
    namespace_dbs = await Namespace.get_namespace_dbs(database, username)
    if namespace_dbs:
        workflow_status_collections = [
            db.get_collection("workflow_status") for db in namespace_dbs  # noqa: E501
        ]
        workflow_stopped = await workflow_status_collections[0].find_one({'workflow_id': workflow_id})  # noqa: E501
        if workflow_stopped or force:
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
            workflow_existing = await workflow_collections[0].find_one({'workflow_id': workflow_id})  # noqa: E501
            if not workflow_existing:
                raise HTTPException(status_code=404, detail="Workflow not found")  # noqa: E501
            for workflow_collection in workflow_collections:
                await workflow_collection.delete_many({'workflow_id': workflow_id})  # noqa: E501
            for collection in collections:
                await collection.delete_many({'workflow_id': workflow_id})
            for logs_collection in logs_collections:
                await logs_collection.delete_many({'task_id': {'$in': task_ids}})  # noqa: E501
            for task_status_collection in task_status_collections:
                await task_status_collection.delete_many({'task_id': {'$in': task_ids}})  # noqa: E501
            return {'message': 'logs deleted'}
        raise HTTPException(status_code=400, detail="Workflow is not stopped yet. Provide query parameter 'force=true' to override this behaviour")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.get('/{workflow_id}/logs', dependencies=[user_role])
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
                '$arrayElemAt': ['$total_count.count', 0]
            }
        }),
    ]
    info(f"Pipeline: {pipeline}")
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    results = dict(ChainMap(*aggregations))
    return results
