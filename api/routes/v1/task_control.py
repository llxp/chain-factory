from asyncio import sleep
from datetime import datetime
from logging import getLogger
from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict, List
from odmantic import AIOEngine
from pymongo.results import InsertOneResult

from .models.workflow import Workflow

from .models.namespace import Namespace

from ...auth.depends import CheckScope, get_username
from .utils import (
    check_namespace_allowed, get_rabbitmq_client, get_rabbitmq_url, get_odm_session  # noqa: E501
)
from .models.task import NewTaskRequest
from framework.src.chain_factory.models.mongodb_models import NodeTasks, Task  # noqa: E501

LOGGER = getLogger(__name__)

api = APIRouter()
user_role = Depends(CheckScope(scope='user'))


@api.post(
    "/new",
    dependencies=[user_role, Depends(check_namespace_allowed)]
)
async def new_task(
    namespace: str,
    task_name: str,
    # node_name: Optional[str] = None,
    json_body: NewTaskRequest = Body(...),
    username: str = Depends(get_username),
    rabbitmq_url: str = Depends(get_rabbitmq_url),
    database: AIOEngine = Depends(get_odm_session),
):
    LOGGER.debug(f"New task: {task_name}")
    input_arguments = json_body.arguments
    LOGGER.debug(f"Arguments: {input_arguments}")
    tags = json_body.tags
    LOGGER.debug(f"Tags: {tags}")
    namespace_entry = await Namespace.get(database, namespace, username)
    LOGGER.info(f"namespace_entry: {namespace_entry}")
    if namespace_entry:
        domain = namespace_entry.domain
        domain_snake_case = domain.replace('.', '_')
        namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa: E501
        if namespace_db is not None:
            node_tasks_collection = namespace_db.get_collection(NodeTasks.__collection__)  # noqa: E501
            if node_tasks_collection is not None:
                node_tasks = await node_tasks_collection.find({"tasks.name": {'$in': [task_name]}}).to_list(None)  # noqa: E501
                node_tasks_objs = [NodeTasks(**node_task) for node_task in node_tasks]  # noqa: E501
                if len(node_tasks_objs) > 0:
                    missing_arguments_tasks: Dict[str, List[str]] = {}
                    invalid_arguments_tasks: Dict[str, List[str]] = {}
                    # iterate over all node/tasks registrations
                    for node_tasks_obj in node_tasks_objs:
                        if node_tasks_obj is not None:
                            tasks = node_tasks_obj.tasks
                            # iterate over all tasks of each node
                            for task_ in tasks:
                                if task_.name == task_name:
                                    arguments_task = task_.arguments
                                    valid_arguments_count = 0
                                    invalid_arguments = []
                                    # check, if a node is available with the given task name and arguments.  # noqa: E501
                                    for input_argument in input_arguments:
                                        if input_argument in arguments_task.keys():  # noqa: E501
                                            valid_arguments_count += 1
                                            LOGGER.debug(f"{input_argument} is valid")  # noqa: E501
                                        else:
                                            invalid_arguments.append(input_argument)  # noqa: E501
                                    missing_arguments = []
                                    for argument in arguments_task.keys():
                                        if argument not in input_arguments:
                                            LOGGER.debug(f"{argument} is not in {input_arguments}")  # noqa: E501
                                            missing_arguments.append(argument)
                                    if valid_arguments_count == len(input_arguments.keys()) and valid_arguments_count == len(arguments_task):  # noqa: E501
                                        vhost = namespace + '_' + domain_snake_case  # noqa: E501
                                        rabbitmq_client = await get_rabbitmq_client(vhost, rabbitmq_url)  # noqa: E501
                                        new_workflow = Workflow(
                                            created_date=datetime.utcnow(),
                                            tags=tags,
                                        )
                                        wf_saved: InsertOneResult = await namespace_db.get_collection(Workflow.__collection__).insert_one(dict(new_workflow))  # noqa: E501
                                        new_task: Task = Task(
                                            name=task_name,
                                            arguments=input_arguments,
                                            tags=json_body.tags,
                                            workflow_id=str(wf_saved.inserted_id),  # noqa: E501
                                        )
                                        # update workflow with workflow id
                                        await namespace_db.get_collection(Workflow.__collection__).update_one(  # noqa: E501
                                            {"_id": wf_saved.inserted_id},
                                            {"$set": dict(workflow_id=str(wf_saved.inserted_id))},  # noqa: E501
                                        )
                                        del new_task.task_id
                                        for _ in range(0, 10):
                                            response = await rabbitmq_client.send(new_task.json())  # noqa: E501
                                            LOGGER.debug(f"Response: {response}")  # noqa: E501
                                            if response:
                                                return "Task created"
                                            else:
                                                await sleep(100)
                                        raise HTTPException(status_code=500, detail="Task could not be created. Probably an error reaching the broker. Please try again.")  # noqa: E501
                                    else:
                                        missing_arguments_tasks[node_tasks_obj.node_name] = missing_arguments  # noqa: E501
                                        invalid_arguments_tasks[node_tasks_obj.node_name] = invalid_arguments  # noqa: E501
                    if len(missing_arguments_tasks) > 0 or len(invalid_arguments_tasks) > 0:  # noqa: E501
                        missing_arguments_tasks_str = "".join(
                            [f"{node_name}.{task_name}: {', '.join(missing_arguments)}\n" for node_name, missing_arguments in missing_arguments_tasks.items()]  # noqa: E501
                        )
                        invalid_arguments_tasks_str = "".join(
                            [f"{node_name}.{task_name}: {', '.join(invalid_arguments)}\n" for node_name, invalid_arguments in invalid_arguments_tasks.items()]  # noqa: E501
                        )
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing arguments:\n{missing_arguments_tasks_str}\nInvalid arguments:\n{invalid_arguments_tasks_str}",  # noqa: E501
                        )
                    raise HTTPException(status_code=400, detail="No node available for the given task")  # noqa: E501
                raise HTTPException(status_code=404, detail="Task not found")
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501
