from fastapi import APIRouter, Depends
from fastapi.security.http import HTTPBearer

from .node import api as node_api
from .task import api as task_api
from .task_control import api as task_control_api
from .namespace import api as namespace_api
from .workflow import api as workflow_api
from .logs import api as logs_api
from .credentials import api as credentials_api


api = APIRouter(dependencies=[Depends(HTTPBearer())])
api.include_router(node_api, tags=["node"])
api.include_router(namespace_api, tags=["namespace"])
api.include_router(task_api, tags=["task"])
api.include_router(task_control_api, tags=["task"])
api.include_router(workflow_api, tags=["workflow"])
api.include_router(logs_api, tags=["logs"])
api.include_router(credentials_api, tags=["credentials"])
