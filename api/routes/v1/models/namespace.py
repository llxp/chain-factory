from typing import List
from pydantic import BaseModel
from odmantic import AIOEngine, Model
from motor.motor_asyncio import AsyncIOMotorDatabase

from ....auth.utils.credentials import get_domain


class Namespace(Model):
    namespace: str = ""
    domain: str = ""
    enabled: bool = True
    allowed_users: List[str]  # list of user ids

    @classmethod
    async def get(
        cls,
        database: AIOEngine,
        namespace: str,
        username: str
    ) -> 'Namespace':
        return await database.find_one(
            Namespace,
            (
                (cls.namespace == namespace) &
                (cls.allowed_users.in_([username]))
            )
        )

    @classmethod
    async def get_multiple(
        cls: type,
        database: AIOEngine,
        username: str
    ) -> List['Namespace']:
        # if domain:
        return await database.find(
            cls,
            (
                (cls.enabled == True) &  # noqa: E712
                # (cls.domain == domain) &
                (cls.allowed_users.in_([username]))
            )
        )
        # return None

    @classmethod
    async def get_allowed(
        cls: type,
        database: AIOEngine,
        username: str
    ) -> List['Namespace']:
        return await cls.get_multiple(database, username)

    @classmethod
    async def is_allowed(
        cls: type,
        namespace: str,
        database: AIOEngine,
        username: str
    ):
        namespaces = await cls.get_multiple(database, username)
        if namespaces:
            namespaces = [
                ns for ns in namespaces if ns.namespace == namespace]
            return len(namespaces) > 0
        return False

    @classmethod
    async def get_namespace_db(
        cls,
        database: AIOEngine,
        namespace: str,
        username: str
    ) -> AsyncIOMotorDatabase:
        namespace_in_db = await database.find_one(cls, (
            (cls.namespace == namespace) &
            (cls.enabled == True) &  # noqa: E712
            (cls.allowed_users.in_([username]))
        ))
        if namespace_in_db:
            domain = namespace_in_db.domain
            domain_snake_case = domain.replace('.', '_')
            db_name = namespace + '_' + domain_snake_case
            return database.client.get_database(db_name)
        return None

    @classmethod
    async def get_namespace_dbs(
        cls,
        database: AIOEngine,
        username: str
    ) -> List[AsyncIOMotorDatabase]:
        domain = await get_domain(username)
        namespaces = await cls.get_multiple(database, domain, username)
        if namespaces:
            return [
                await cls.get_namespace_db(
                    database, namespace.namespace, username)
                for namespace in namespaces
            ]
        return []

    @classmethod
    async def get_filtered_namespace_dbs(
        cls,
        database: AIOEngine,
        username: str,
        namespace: str
    ) -> List[AsyncIOMotorDatabase]:
        namespaces = await cls.get_multiple(database, username)
        if namespaces:
            return [
                await cls.get_namespace_db(
                    database, ns.namespace, username)
                for ns in namespaces if namespace == "default" or ns.namespace == namespace  # noqa: E501
            ]
        return []


class NamespaceCreatedResponse(BaseModel):
    namespace: str = ""
