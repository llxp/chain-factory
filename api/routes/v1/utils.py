from http.client import HTTPException
from aioredis import Redis
from fastapi import Request
from datetime import datetime
from cryptography.fernet import Fernet

from framework.src.chain_factory.task_queue.common.settings import (
    heartbeat_redis_key, heartbeat_sleep_time
)
from framework.src.chain_factory.task_queue.models.redis_models import (
    Heartbeat
)
from framework.src.chain_factory.task_queue.wrapper.rabbitmq import RabbitMQ


def default_namespace(namespace):
    return namespace == "default" or namespace == "all"


def has_pagination(page, page_size):
    return page is not None and page_size is not None


def get_page_size(page_size):
    return page_size if page_size > 0 else 1


def skip_stage(page, page_size):
    stage = {}
    if has_pagination(page, page_size):
        stage["$skip"] = page * get_page_size(page_size)
    return stage


def limit_stage(page, page_size):
    stage = {}
    if has_pagination(page, page_size):
        stage["$limit"] = get_page_size(page_size)
    return stage


def sort_stage(sort_by, sort_order):
    stage = {}
    sortable_fields = [
        'created_date',
        'entry_task.name',
        'workflow.workflow_id',
        'workflow.namespace',
        'workflow.tags'
    ]
    if sort_by in sortable_fields and sort_order in ["asc", "desc"]:
        stage['$sort'] = {
            sort_by: 1 if sort_order == 'asc' else -1
        }
    return stage


def lookup(from_: str, local_field: str, foreign_field: str, as_: str):
    return {
        '$lookup': {
            'from': from_,
            'localField': local_field,
            'foreignField': foreign_field,
            'as': as_
        }
    }


def lookup_workflow_status(local_field: str, as_: str):
    return lookup('workflow_status', local_field, 'workflow_id', as_)


def lookup_logs(local_field: str, as_: str):
    return lookup('logs', local_field, 'task_id', as_)


def match(fields):
    return {"$match": fields}


def unwind(field):
    return {"$unwind": field}


def project(fields):
    return {"$project": fields}


def facet(fields):
    return {"$facet": fields}


def and_(fields):
    if isinstance(fields, list):
        return {"$and": fields}
    return {"$and": [fields]}


def map(fields):
    return {"$map": fields}


def add_fields(fields):
    return {"$addFields": fields}


async def node_active(node_name: str, namespace: str, redis_client: Redis):
    redis_key = heartbeat_redis_key + "_" + namespace + "_" + node_name
    node_status_bytes = redis_client.get(redis_key)
    if node_status_bytes is not None:
        node_status_string = node_status_bytes.decode("utf-8")
        if len(node_status_string) > 0:
            heartbeat_status: Heartbeat = Heartbeat.from_json(
                node_status_string)
            last_time_seen = heartbeat_status.last_time_seen
            now = datetime.utcnow()
            diff = now - last_time_seen
            if diff.total_seconds() <= (heartbeat_sleep_time * 2):
                return True
    return False


def get_rabbitmq_client(namespace: str, rabbitmq_url: str):
    return RabbitMQ(
        url=rabbitmq_url,
        queue_name=namespace + "_" + "task_queue",
        rmq_type="publisher"
    )


async def get_odm_session(request: Request):
    try:
        return request.state.odm_session
    except AttributeError:
        raise HTTPException(status_code=500, detail="ODM session not set")


async def get_redis_client(request: Request):
    try:
        return request.state.redis_client
    except AttributeError:
        raise HTTPException(status_code=500, detail="Redis client not set")


async def get_rabbitmq_management_api(request: Request):
    try:
        return request.state.rabbitmq_management_api
    except AttributeError:
        raise HTTPException(
            status_code=500, detail="RabbitMQ management API not set")


async def get_rabbitmq_url(request: Request):
    try:
        return request.state.rabbitmq_url
    except AttributeError:
        raise HTTPException(
            status_code=500, detail="RabbitMQ URL not set")


def encrypt(message: bytes, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    return Fernet(key_bytes).encrypt(message_bytes)


def decrypt(token: str, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    token_bytes = token.encode('utf-8')
    return Fernet(key_bytes).decrypt(token_bytes)
