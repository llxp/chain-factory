from fastapi import APIRouter, Depends, Body
from typing import Optional

from ...auth.utils.credentials import get_domain
from ...auth.depends import CheckScope, get_username
from .utils import (
    check_namespace_allowed, get_rabbitmq_client, get_rabbitmq_url
)
from .models.task import NewTaskRequest, TaskCreatedResponse
from framework.src.chain_factory.task_queue.models.mongodb_models import Task


api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.post(
    "/new_task",
    dependencies=[user_role, Depends(check_namespace_allowed)]
)
async def new_task(
    namespace: str,
    task: str,
    node_name: Optional[str] = None,
    json_body: Optional[NewTaskRequest] = Body(...),
    username: str = Depends(get_username),
    rabbitmq_url: str = Depends(get_rabbitmq_url)
):
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
    rabbitmq_client = await get_rabbitmq_client(
        vhost, namespace, rabbitmq_url)
    for i in range(0, 1):
        await rabbitmq_client.send(new_task.json())
    return TaskCreatedResponse(message="Task created")
