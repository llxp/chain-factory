from http.client import HTTPException
from fastapi import APIRouter, Depends, Body
from typing import Optional
from odmantic import AIOEngine

from ...auth.utils.credentials import get_domain
from ...auth.depends import CheckScope, get_username
from .utils import get_rabbitmq_client, get_odm_session, get_rabbitmq_url
from .models.namespace import Namespace
from .models.task import NewTaskRequest, TaskCreatedResponse
from framework.src.chain_factory.task_queue.models.mongodb_models import Task


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.post("/new_task", dependencies=[user_role])
async def new_task(
    namespace: str,
    task: str,
    node_name: str,
    json_body: Optional[NewTaskRequest] = Body(...),
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    rabbitmq_url: str = Depends(get_rabbitmq_url)
):
    if await Namespace.is_allowed(namespace, database, username):
        new_task: Task = Task(
            name=task,
            arguments=json_body.arguments,
            node_names=[node_name] if (
                node_name and node_name != 'default') else [],
            tags=json_body.tags,
        )
        domain = await get_domain(username)
        domain_snake_case = domain.replace('.', '_')
        vhost = namespace + '_' + domain_snake_case
        rabbitmq_client = get_rabbitmq_client(vhost, rabbitmq_url)
        rabbitmq_client.send(new_task.json())
        return TaskCreatedResponse(message="Task created")
    raise HTTPException(
        status_code=404, detail="Namespace not found or you don't have access")
