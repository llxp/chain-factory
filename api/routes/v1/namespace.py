from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine
from ...auth.depends import CheckScope, get_username
from .utils import get_odm_session
from .models.namespace import Namespace, NamespaceCreatedResponse
from ...auth.utils.credentials import get_domain


api = APIRouter()
user_role = Depends(CheckScope(scope="user"))


@api.get('/namespaces', dependencies=[user_role])
async def namespaces(
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    return await database.find(Namespace, (
        Namespace.allowed_users.in_([username]) & (Namespace.enabled)
    ))


@ api.post('/namespaces', dependencies=[user_role])
async def create_namespace(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    if namespace == '':
        raise HTTPException(
            status_code=400, detail="Namespace cannot be empty")
    namespace_exists = await database.find_one(
        Namespace,
        Namespace.namespace == namespace
    )
    if not namespace_exists:
        namespace_result = await database.save(Namespace(
            namespace=namespace,
            domain=await get_domain(username),
            enabled=True,
            created_date=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            allowed_users=[username]
        ))
        print(namespace_result)
        return NamespaceCreatedResponse(
            namespace=str(namespace_result.inserted_id)
        )
    else:
        raise HTTPException(
            status_code=400, detail="Namespace already exists")
