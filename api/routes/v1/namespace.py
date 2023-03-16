from datetime import datetime
from logging import error, info
from fastapi import APIRouter, Depends, HTTPException
from odmantic import AIOEngine
from redis import Redis
from amqpstorm.management import ManagementApi, ApiError
from ...auth.depends import CheckScope, get_breakglass_domain, get_breakglass_username, get_username  # noqa: E501
from .utils import get_odm_session, get_rabbitmq_management_api, get_redis_client  # noqa: E501
from .models.namespace import Namespace
from ...auth.utils.credentials import get_domain


api = APIRouter()
user_role = Depends(CheckScope(scope="user"))
namespace_admin_role = Depends(CheckScope(scope="namespace_admin"))


@api.get('/active', dependencies=[user_role])
async def namespaces(
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    namespaces = await Namespace.get_allowed(database, username)
    namespaces_dicts = [ns.dict() for ns in namespaces]
    for namespace in namespaces_dicts:
        del namespace['id']
        del namespace['enabled']
        del namespace['domain'],
    return namespaces_dicts


@api.get('/disabled', dependencies=[user_role])
async def disabled_namespaces(
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
):
    namespaces = await Namespace.get_disabled(database, username)
    namespaces_dicts = [ns.dict() for ns in namespaces]
    for namespace in namespaces_dicts:
        del namespace['id']
        del namespace['enabled']
        del namespace['domain'],
    return namespaces_dicts


@api.post('/{namespace}', dependencies=[user_role])
async def create_namespace(
    namespace: str,
    database: AIOEngine = Depends(get_odm_session),
    username: str = Depends(get_username),
    breakglass_username: str = Depends(get_breakglass_username),
    breakglass_domain: str = Depends(get_breakglass_domain),
):
    if namespace == '':
        raise HTTPException(status_code=400, detail="Namespace cannot be empty")  # noqa: E501
    namespace_exists = await database.find_one(Namespace, Namespace.namespace == namespace)  # noqa: E501
    if not namespace_exists:
        username_lower = username.lower()
        domain = await get_domain(username)
        domain_lower = domain.lower()
        now = datetime.utcnow()
        breakglass_user = f"{breakglass_username}@{breakglass_domain}"
        allowed_users = [username_lower, breakglass_user] if username_lower != breakglass_user else [username_lower]  # noqa: E501
        namespace_result = await database.save(Namespace(
            namespace=namespace,
            domain=domain_lower,
            enabled=True,
            created_at=now,
            updated_at=now,
            allowed_users=allowed_users,
            creator=username_lower,
        ))
        info(f"Created namespace {namespace_result.namespace}")
        info(f"Allowed users {namespace_result.allowed_users}")
        info(f"Domain {namespace_result.domain}")
        if namespace_result and namespace_result.id:
            return "Namespace created successfully"
        raise HTTPException(status_code=500, detail="Namespace creation failed")  # noqa: E501
    raise HTTPException(status_code=409, detail="Namespace already exists")


@api.put(
    '/{namespace}/add_user/{username}',
    dependencies=[user_role]
)
async def allow_user_to_namespace(
    namespace: str,
    username: str,
    current_user: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_obj = await Namespace.get(database, namespace, current_user)
    if namespace_obj:
        if username not in namespace_obj.allowed_users:
            username_lower = username.lower()
            namespace_obj.allowed_users.append(username_lower)
            info(f"adding {username_lower} to {namespace_obj.namespace}")
            namespace_obj.updated_at = datetime.utcnow()
            await database.save(namespace_obj)
            return "User allowed to namespace"
        raise HTTPException(status_code=409, detail="User already allowed to namespace")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.put(
    '/{namespace}/remove_user/{username}',
    dependencies=[user_role]
)
async def remove_user_from_namespace(
    namespace: str,
    username: str,
    current_user: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_obj = await Namespace.get(database, namespace, current_user)
    if namespace_obj:
        if username in namespace_obj.allowed_users:
            username_lower = username.lower()
            namespace_obj.allowed_users.remove(username_lower)
            info(f"removing {username_lower} from {namespace_obj.namespace}")
            namespace_obj.updated_at = datetime.utcnow()
            await database.save(namespace_obj)
            return "User removed from namespace"
        raise HTTPException(status_code=404, detail="User not yet allowed to namespace")  # noqa: E501
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.delete('/{namespace}/disable', dependencies=[user_role])
async def disable_namespace(
    namespace: str,
    username: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_obj = await Namespace.get(database, namespace, username)
    if namespace_obj:
        namespace_obj.enabled = False
        namespace_obj.updated_at = datetime.utcnow()
        await database.save(namespace_obj)
        return "Namespace disabled"
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.delete('/{namespace}/delete', dependencies=[user_role])
async def delete_namespace(
    namespace: str,
    username: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
    redis_client: Redis = Depends(get_redis_client),
    rabbitmq_management_api: ManagementApi = Depends(get_rabbitmq_management_api),  # noqa: E501
):
    namespace_obj = await Namespace.get_disabled_one(database, namespace, username)  # noqa: E501
    if namespace_obj:
        # MongoDB section
        # --------------------------------
        namespace_db = await Namespace.get_namespace_db(database, namespace, username)  # noqa
        if namespace_db is not None:
            await database.client.drop_database(namespace_db)
            info(f"Deleted namespace db {namespace_db} in mongodb")
        # --------------------------------
        # Redis section
        # --------------------------------
        email_snake_case = username.replace('.', '_').replace('@', '_')
        redis_username = email_snake_case + '_' + namespace
        redis_client.acl_deluser(redis_username)
        info(f"Deleted namespace {namespace} in redis")
        # --------------------------------
        # RabbitMQ section
        # --------------------------------
        # 1. delete vhost
        domain_snake_case = namespace_obj.domain.replace('.', '_')
        vhost_name = namespace + '_' + domain_snake_case
        try:
            rabbitmq_management_api.virtual_host.delete(vhost_name)
            info(f"Deleted namespace {namespace} in rabbitmq")
        except ApiError as e:
            error(f"Error deleting namespace {namespace} in rabbitmq: {e}")
        # 2. delete user
        rabbitmq_username = email_snake_case + '_' + namespace
        try:
            rabbitmq_management_api.user.delete(rabbitmq_username)
            info(f"Deleted namespace {namespace} in rabbitmq")
        except ApiError as e:
            error(f"Error deleting username {rabbitmq_username} for namespace {namespace} in rabbitmq: {e}")  # noqa: E501
        # --------------------------------
        await database.delete(namespace_obj)
        # delete namespace obj from mongodb
        info(f"Deleted namespace {namespace} in mongodb")
        return "Namespace deleted"
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.put('/{namespace}/enable', dependencies=[user_role])
async def enable_namespace(
    namespace: str,
    username: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
):
    namespace_obj = await Namespace.get(database, namespace, username, False)
    if namespace_obj:
        namespace_obj.enabled = True
        namespace_obj.updated_at = datetime.utcnow()
        await database.save(namespace_obj)
        return "Namespace enabled"
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501


@api.put('/{namespace}/rename', dependencies=[user_role])
async def rename_namespace(
    namespace: str,
    new_namespace: str,
    username: str = Depends(get_username),
    database: AIOEngine = Depends(get_odm_session),
):
    # TODO: please review this, if still necessary/useful
    namespace_obj = await Namespace.get(database, namespace, username)
    if namespace_obj:
        namespace_obj.namespace = new_namespace
        namespace_obj.updated_at = datetime.utcnow()
        await database.save(namespace_obj)
        return "Namespace renamed"
    raise HTTPException(status_code=401, detail="Namespace does not exist or you do not have access")  # noqa: E501
