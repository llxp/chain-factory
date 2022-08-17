from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine
from framework.src.chain_factory.task_queue.common.settings import (
    task_control_channel_redis_key
)
from framework.src.chain_factory.task_queue.models.redis_models import (
    TaskControlMessage
)
from framework.src.chain_factory.task_queue.models.mongodb_models import (
    Task,
    TaskWorkflowAssociation
)
from framework.src.chain_factory.task_queue.wrapper.\
    redis_client import RedisClient
from ...auth.depends import CheckScope
from .utils import get_allowed_namespace, get_odm_session, get_redis_client, get_username, get_rabbitmq_url, get_rabbitmq_client  # noqa: E501
from .models.namespace import Namespace


api = APIRouter()
workflow_controller_role = Depends(CheckScope(scope='workflow_controller'))


@api.post('/stop_workflow', dependencies=[workflow_controller_role])
async def stop_workflow(
    namespace: str,
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: RedisClient = Depends(get_redis_client),
    username: str = Depends(get_username),
):
    namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa: E501
    if namespace_db is not None:
        workflow_status_collection = namespace_db.get_collection("workflow_status")  # noqa: E501
        if workflow_status_collection is not None:
            redis_client.publish(
                namespace + '_' + task_control_channel_redis_key,
                TaskControlMessage(
                    workflow_id=workflow_id,
                    command='stop'
                ).json())
            if not (
                await workflow_status_collection.find_one({
                        "$and": [
                            {'namespace': namespace},
                            {'workflow_id': workflow_id}
                        ]
                    })
            ):
                await workflow_status_collection.insert_one(dict(
                    workflow_id=workflow_id,
                    namespace=namespace,
                    status='Stopped'
                ))
                return "Workflow stopped"
            return 'Workflow already stopped'
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.post('/abort_workflow', dependencies=[workflow_controller_role])
async def abort_workflow(
    namespace: str,
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: RedisClient = Depends(get_redis_client),
    username: str = Depends(get_username),
):
    namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa: E501
    if namespace_db is not None:
        workflow_status_collection = namespace_db.get_collection("workflow_status")  # noqa: E501
        if workflow_status_collection is not None:
            redis_key = namespace + '_' + task_control_channel_redis_key
            redis_client.publish(
                redis_key,
                TaskControlMessage(
                    workflow_id=workflow_id,
                    command='abort'
                ).json())
            if not (
                await workflow_status_collection.find_one({
                    "$and": [
                        {'namespace': namespace},
                        {'workflow_id': workflow_id}
                    ]
                })
            ):
                await workflow_status_collection.insert_one(dict(
                    workflow_id=workflow_id,
                    namespace=namespace,
                    status='Stopped'
                ))
                return "Workflow aborted"
            raise HTTPException(status_code=400, detail="Workflow already stopped")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.post('/restart_workflow', dependencies=[workflow_controller_role])
async def restart_workflow(
    namespace: str,
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: RedisClient = Depends(get_redis_client),
    username: str = Depends(get_username),
    rabbitmq_url: str = Depends(get_rabbitmq_url),
    namespace_obj: Namespace = Depends(get_allowed_namespace)
):
    namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa: E501
    if namespace_db is not None:
        workflow_status_collection = namespace_db.get_collection("workflow_status")  # noqa: E501
        if workflow_status_collection is not None:
            # first send abort message, if a task is still running
            redis_client.publish(
                namespace + '_' + task_control_channel_redis_key,
                TaskControlMessage(
                    workflow_id=workflow_id,
                    command='abort'
                ).json())
            if (
                not await workflow_status_collection.find_one({
                    "$and": [
                        {'namespace': namespace},
                        {'workflow_id': workflow_id}
                    ]
                })
            ):
                await workflow_status_collection.insert_one(dict(
                    workflow_id=workflow_id,
                    namespace=namespace
                ))
            # figure out the first task in the workflow
            task_collection = namespace_db.get_collection("task_workflow_association")  # noqa: E501
            if task_collection is not None:
                first_task = await task_collection.find_one({
                    '$and': [
                        {'workflow_id': workflow_id},
                        {'task.parent_task_id': ''}
                    ]
                })
                if first_task is not None:
                    first_task_obj = TaskWorkflowAssociation(**first_task)
                    if first_task_obj is not None:
                        domain = namespace_obj.domain
                        domain_snake_case = domain.replace('.', '_')
                        vhost = namespace + '_' + domain_snake_case  # noqa: E501
                        rabbitmq_client = await get_rabbitmq_client(vhost, namespace, rabbitmq_url)  # noqa: E501
                        new_task: Task = Task(
                            name=first_task_obj.task.name,
                            arguments=first_task_obj.task.arguments,
                            node_names=first_task_obj.task.node_names,
                            tags=first_task_obj.task.tags,
                        )
                        response = await rabbitmq_client.send(new_task.json())  # noqa: E501
                        if response:
                            return "Workflow restarted"
                raise HTTPException(status_code=500, detail="Failed to restart workflow")  # noqa: E501
            raise HTTPException(status_code=400, detail="Workflow already stopped")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501
