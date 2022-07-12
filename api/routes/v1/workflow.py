from collections import ChainMap
from logging import debug
from re import compile, UNICODE
from bson.regex import Regex
from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorCollection

from ...auth.depends import CheckScope, get_username
from .utils import (
    check_namespace_allowed, get_allowed_namespaces,
    get_odm_session, match, project, lookup,
    sort_stage, skip_stage, limit_stage,
    lookup_logs, default_namespace, lookup_workflow_status
)
from .models.namespace import Namespace


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.get('/workflows', dependencies=[user_role])
async def workflows(
    namespace: str,
    namespaces: List[str] = Depends(get_allowed_namespaces),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
):
    namespace_dbs = await Namespace.get_filtered_namespace_dbs(database, username, namespace)  # noqa: E501

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
                "workflow": {
                    "$first": "$workflow"
                },
                'created_date': {
                    '$first': '$created_dates'
                }
            }),
            *search_stage(),
            project({
                'entry_task': {'$first': '$tasks'},
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
                        {'$first': '$status.status'},
                        'Running'
                    ]
                },
            }),
            project({'status._id': 0}),
            {
                "$facet": {
                    "workflows": [
                        stage2
                        for stage2 in [
                            sort_stage(sort_by, sort_order),
                            skip_stage(page, page_size),
                            limit_stage(page, page_size)
                        ]
                        if stage2 != {}
                    ],
                    "total_count": [{"$count": "count"}],
                }
            },
            project({
                "workflows": 1,
                "total_count": {
                    '$ifNull': [{"$first": "$total_count.count"}, 0]
                },
                'count': {'$size': '$workflows'}
            })
        ] if stage != {}
    ]

    collections: List[AsyncIOMotorCollection] = [
        db.get_collection("workflow") for db in namespace_dbs
    ]
    # workflow_tasks = collection.aggregate(pipeline)
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    return aggregations[0]


@api.get(
    '/workflow_tasks',
    dependencies=[user_role, Depends(check_namespace_allowed)]
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
                '$first': '$total_count.count'
            }
        })
    ]
    namespace_db = await Namespace.get_namespace_db(
        database, namespace, username)
    collection = namespace_db.get_collection("task_workflow_association")
    log_result = await collection.aggregate(pipeline).to_list(1)
    return log_result[0]


@api.get('/workflow_status', dependencies=[user_role])
async def workflow_status(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[str] = Depends(get_allowed_namespaces),
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
                        '$first': "$workflow_status.status"
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
                                    '$first': {
                                        '$filter': {
                                            'input': "$task_status1",
                                            'cond': {
                                                '$eq': [
                                                    "$$this.task_id",
                                                    "$$row.task.task_id"
                                                ]
                                            }
                                        }
                                    }
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


@api.get('/workflow_metrics', dependencies=[user_role])
async def workflow_metrics(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    namespaces: List[str] = Depends(get_allowed_namespaces),
    username: str = Depends(get_username),
):
    namespace_dbs = await Namespace.get_namespace_dbs(database, username)
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
                        '$first': "$workflow_status.status"
                    },
                    'Running'
                ]
            },
            'workflow_id': 1,
            'created_date': {
                '$ifNull': [
                    {
                        '$toString': {
                            '$last': "$workflow_status.created_date"
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
    debug(pipeline)
    aggregations = [
        doc for collection in collections
        async for doc in collection.aggregate(pipeline)
    ]
    results = dict(ChainMap(*aggregations))
    return results
