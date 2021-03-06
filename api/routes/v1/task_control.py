from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Optional
from odmantic import AIOEngine

from .models.namespace import Namespace

from ...auth.depends import CheckScope, get_username
from .utils import (
    check_namespace_allowed, get_rabbitmq_client, get_rabbitmq_url, get_odm_session  # noqa: E501
)
from .models.task import NewTaskRequest, TaskCreatedResponse
from framework.src.chain_factory.task_queue.models.mongodb_models import NodeTasks, Task  # noqa: E501


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
    rabbitmq_url: str = Depends(get_rabbitmq_url),
    database: AIOEngine = Depends(get_odm_session),
):
    new_task: Task = Task(
        name=task,
        arguments=json_body.arguments,
        node_names=[node_name] if (
            node_name and node_name != 'default') else [],
        tags=json_body.tags,
    )
    namespace_entry = await Namespace.get(database, namespace, username)
    if namespace_entry:
        domain = namespace_entry.domain
        domain_snake_case = domain.replace('.', '_')
        namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa: E501
        if namespace_db is not None:
            node_tasks_collection = namespace_db.get_collection(NodeTasks.__collection__)  # noqa: E501
            if node_tasks_collection is not None:
                node_tasks = await node_tasks_collection.find(
                    {
                        "namespace": namespace,
                        "tasks.name": {'$in': [task]},
                    }
                ).to_list(None)
                node_tasks_objs = [NodeTasks(**node_task) for node_task in node_tasks]  # noqa: E501
                input_arguments = new_task.arguments
                if len(node_tasks_objs) > 0:
                    for node_tasks_obj in node_tasks_objs:
                        if node_tasks_obj is not None:
                            tasks = node_tasks_obj.tasks
                            for task_ in tasks:
                                if task_.name == task:
                                    arguments_task = task_.arguments
                                    print(arguments_task)
                                    print(input_arguments)
                                    valid_arguments_count = 0
                                    # check, if a node is available with the given task name and arguments.  # noqa: E501
                                    for input_argument in input_arguments:
                                        if input_argument in arguments_task.keys():  # noqa: E501
                                            valid_arguments_count += 1
                                            print(f"{input_argument} is valid")  # noqa: E501
                                        else:
                                            print(f"{input_argument} is not valid")  # noqa: E501
                                            raise HTTPException(
                                                status_code=400,
                                                detail={
                                                    'message': f"Argument {input_argument} does not exist for task {task}",  # noqa: E501
                                                    'invalid_arguments': [input_argument],  # noqa: E501
                                                },
                                            )
                                    missing_arguments = []
                                    for argument in arguments_task.keys():
                                        if argument not in input_arguments:
                                            print(f"{argument} is not valid")
                                            missing_arguments.append(argument)
                                    if len(missing_arguments) > 0:
                                        raise HTTPException(
                                            status_code=400,
                                            detail={
                                                'message': f"Arguments {missing_arguments} is missing for task {task}",  # noqa: E501
                                                'missing_arguments': [missing_arguments],  # noqa: E501
                                            },
                                        )
                                    if valid_arguments_count == len(input_arguments.keys()) and valid_arguments_count == len(arguments_task):  # noqa: E501
                                        vhost = namespace + '_' + domain_snake_case  # noqa: E501
                                        rabbitmq_client = await get_rabbitmq_client(vhost, namespace, rabbitmq_url)  # noqa: E501
                                        response = await rabbitmq_client.send(new_task.json())  # noqa: E501
                                        if response:
                                            return TaskCreatedResponse(message="Task created")  # noqa: E501
                    raise HTTPException(status_code=400, detail="No node available for the given task")  # noqa: E501
                raise HTTPException(status_code=400, detail="Task not found")
    raise HTTPException(status_code=400, detail="Namespace not found or not allowed")  # noqa: E501
