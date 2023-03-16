from distutils.log import debug
from logging import info
from fastapi import HTTPException
from redis import StrictRedis
from redis_sentinel_url import connect as rsu_connect
from fastapi import Request, Depends
from datetime import datetime
from cryptography.fernet import Fernet
from odmantic import AIOEngine

from framework.src.chain_factory.common.settings import heartbeat_redis_key
from framework.src.chain_factory.common.settings import heartbeat_sleep_time
from framework.src.chain_factory.models.redis_models import Heartbeat  # noqa: E501
from framework.src.chain_factory.wrapper.rabbitmq import RabbitMQ
from ...auth.depends import get_username
from .models.namespace import Namespace


rabbitmq_connection_pool = {}


def default_namespace(namespace):
    return namespace == "default" or namespace == "all"


def has_pagination(page: int, page_size: int):
    return page != -1 and page_size != -1


def get_page_size(page_size: int):
    return page_size if page_size > 0 else 1


def has_begin_end(begin: str, end: str):
    return begin != "" and end != ""


def skip_stage(page: int, page_size: int):
    stage = {}
    if has_pagination(page, page_size):
        stage["$skip"] = page * get_page_size(page_size)
    return stage


def limit_stage(page: int, page_size: int):
    stage = {}
    if has_pagination(page, page_size):
        stage["$limit"] = get_page_size(page_size)
    return stage


def begin_end_stage(begin: str, end: str, stage: dict = {}):
    if has_begin_end(begin, end):
        begin_int = int(begin)
        end_int = int(end)
        begin_datetime = datetime.fromtimestamp(begin_int)
        end_datetime = datetime.fromtimestamp(end_int)
        if "$match" not in stage:
            stage["$match"] = {
                "$and": []
            }
        stage["$match"]["$and"].append({
            'created_date': {
                '$gte': begin_datetime,
                '$lte': end_datetime
            }
        })
    return stage


def sort_stage(sort_by, sort_order):
    stage = {}
    sortable_fields = [
        'created_date',
        'entry_task.name',
        'workflow.workflow_id',
        # 'workflow.namespace',
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


async def node_active(
    node_name: str,
    namespace: str,
    domain: str,
    redis_client: StrictRedis
):
    domain_snake_case = domain.replace(".", "_")
    redis_key = (
        namespace + "_" +
        domain_snake_case + "_" +
        heartbeat_redis_key + "_" +
        node_name
    )
    info("Checking node active: " + redis_key)
    node_status_bytes = redis_client.get(redis_key)
    if node_status_bytes is not None:
        node_status_string = node_status_bytes.decode("utf-8")
        info("Node heartbeat: " + node_status_string)
        if len(node_status_string) > 0:
            heartbeat_status: Heartbeat = Heartbeat.parse_raw(
                node_status_string)
            last_time_seen = heartbeat_status.last_time_seen
            info(f"last_time_seen: {last_time_seen}")
            now = datetime.utcnow()
            info(f"now: {now}")
            diff = now - last_time_seen
            info(f"diff: {diff}")
            info(f"diff.seconds: {diff.total_seconds()}")
            if diff.total_seconds() <= (heartbeat_sleep_time * 30):
                info("Node is active")
                return True
    info("Node is not active")  # TODO: Send Email if Node is not active
    return False


async def get_rabbitmq_client(vhost: str, rabbitmq_url: str) -> RabbitMQ:
    if len(rabbitmq_url) > 0 and len(vhost) > 0:
        if vhost.startswith("/"):
            vhost = vhost[1:]
        if rabbitmq_url.endswith("/"):
            url = rabbitmq_url + vhost
        else:
            url = rabbitmq_url + "/" + vhost
    else:
        url = rabbitmq_url
    debug("Getting rabbitmq client for vhost: " + vhost)
    debug(f"final rabbitmq url: {url}")
    if rabbitmq_connection_pool.get(url) is None:
        client = RabbitMQ(
            url=url,
            queue_name="it_queue",
            rmq_type="publisher",
        )
        await client.init()
        rabbitmq_connection_pool[url] = client
    return rabbitmq_connection_pool[url]


async def get_odm_session(request: Request):
    try:
        return request.state.odm_session
    except AttributeError:
        raise HTTPException(status_code=500, detail="ODM session not set")


async def get_allowed_namespaces(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    if namespace == "default" or namespace == "all":
        return await Namespace.get_allowed(database, username)
    if namespace_obj := await Namespace.get(database, namespace, username):
        return [namespace_obj]
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


async def get_allowed_namespaces_even_disabled(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    if namespace == "default" or namespace == "all":
        return await Namespace.get_allowed(database, username, True)
    if namespace_obj := await Namespace.get_disabled_one(database, namespace, username):  # noqa: E501
        return [namespace_obj]
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


async def check_namespace_allowed(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    if not await Namespace.is_allowed(namespace, database, username):
        raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


async def check_namespace_allowed_even_disabled(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    if not await Namespace.is_allowed(namespace, database, username, True):
        raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


async def get_allowed_namespace(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    namespace_obj = await Namespace.get(database, namespace, username)
    if namespace_obj is None:
        raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501
    return namespace_obj


async def get_redis_client(request: Request) -> StrictRedis:
    try:
        redis_url = request.state.redis_url
        _, client = rsu_connect(redis_url)
        return client  # type: ignore
    except AttributeError:
        raise HTTPException(status_code=500, detail="Redis url not set")


async def get_rabbitmq_management_api(request: Request):
    try:
        return request.state.rabbitmq_management_api
    except AttributeError:
        raise HTTPException(status_code=500, detail="RabbitMQ management API not set")  # noqa: E501


async def get_rabbitmq_url(request: Request) -> str:
    try:
        return request.state.rabbitmq_url
    except AttributeError:
        raise HTTPException(status_code=500, detail="RabbitMQ URL not set")  # noqa: E501


def encrypt(message: str, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    return Fernet(key_bytes).encrypt(message_bytes)


def decrypt(token: str, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    token_bytes = token.encode('utf-8')
    return Fernet(key_bytes).decrypt(token_bytes)
