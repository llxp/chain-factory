from fastapi import APIRouter

from .node import api as node_api
from .task import api as task_api
from .task_control import api as task_control_api
from .namespace import api as namespace_api
from .workflow import api as workflow_api
from .credentials import api as credentials_api
from .workflow_control import api as workflow_control_api

api = APIRouter()
api.include_router(node_api, tags=["node"], prefix="/node")
api.include_router(namespace_api, tags=["namespace"], prefix="/namespaces")
api.include_router(task_api, tags=["tasks"], prefix="/tasks")
api.include_router(task_control_api, tags=["tasks"], prefix="/tasks")
api.include_router(workflow_api, tags=["workflows"], prefix="/workflows")
api.include_router(credentials_api, tags=["namespace"], prefix="/namespaces")
api.include_router(workflow_control_api, tags=["workflows"], prefix="/workflows")  # noqa: E501
