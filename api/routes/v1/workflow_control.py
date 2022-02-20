from datetime import datetime
from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from framework.src.chain_factory.task_queue.common.settings import (
    task_control_channel_redis_key
)
from framework.src.chain_factory.task_queue.models.mongodb_models import (
    WorkflowStatus
)
from framework.src.chain_factory.task_queue.models.redis_models import (
    TaskControlMessage
)
from framework.src.chain_factory.task_queue.wrapper.\
    redis_client import RedisClient
from ...auth.depends import CheckScope
from .utils import get_odm_session, get_redis_client


api = APIRouter()
workflow_controller_role = Depends(CheckScope(scope='workflow_controller'))


@ api.post('/stop_workflow', dependencies=[workflow_controller_role])
async def stop_workflow(
    namespace: str,
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: RedisClient = Depends(get_redis_client),
):
    redis_client.publish(
        namespace + '_' + task_control_channel_redis_key,
        TaskControlMessage(
            workflow_id=workflow_id,
            command='stop'
        ).json())
    if not (
        await database.find_one(WorkflowStatus, (
            (WorkflowStatus.namespace == namespace) &
            (WorkflowStatus.workflow_id == workflow_id)
        ))
    ):
        await database.save(WorkflowStatus(
            workflow_id=workflow_id,
            namespace=namespace,
            status='Stopped',
            created_date=datetime.utcnow()
        ))
    return 'OK'


@ api.post('/abort_workflow', dependencies=[workflow_controller_role])
async def abort_workflow(
    namespace: str,
    workflow_id: str,
    database: AIOEngine = Depends(get_odm_session),
    redis_client: RedisClient = Depends(get_redis_client),
):
    redis_key = namespace + '_' + task_control_channel_redis_key
    redis_client.publish(
        redis_key,
        TaskControlMessage(
            workflow_id=workflow_id,
            command='abort'
        ).json())
    if not (
        await database.find_one(WorkflowStatus, (
            (WorkflowStatus.workflow_id == workflow_id) &
            (WorkflowStatus.namespace == namespace)
        ))
    ):
        await database.save(WorkflowStatus(
            workflow_id=workflow_id,
            namespace=namespace,
            status='Stopped'
        ))
    return 'OK'
