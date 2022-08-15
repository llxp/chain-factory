from logging import info
from datetime import datetime
from typing import List
from odmantic import AIOEngine, Model
from motor.motor_asyncio import AsyncIOMotorDatabase


class Namespace(Model):
    namespace: str = ""
    domain: str = ""
    enabled: bool = True
    allowed_users: List[str]  # list of user ids
    created_at: datetime
    updated_at: datetime
    creator: str

    @classmethod
    async def get(
        cls,
        database: AIOEngine,
        namespace: str,
        username: str,
        enabled: bool = True,
    ) -> 'Namespace':
        username = username.lower()
        return await database.find_one(
            cls,
            (
                (cls.namespace == namespace) &
                (cls.allowed_users.in_([username])) &
                (cls.enabled == enabled)  # noqa: E712
            )
        )

    @classmethod
    async def get_disabled_one(
        cls,
        database: AIOEngine,
        namespace: str,
        username: str,
    ) -> 'Namespace':
        username = username.lower()
        return await database.find_one(
            cls,
            (
                (cls.namespace == namespace) &
                (cls.allowed_users.in_([username]))
            )
        )

    @classmethod
    async def get_multiple(
        cls: type,
        database: AIOEngine,
        username: str,
        enabled: bool = True,
    ) -> List['Namespace']:
        username = username.lower()
        return await database.find(
            cls,
            (
                (cls.enabled == enabled) &  # noqa: E712
                (cls.allowed_users.in_([username]))
            )
        )

    @classmethod
    async def get_multiple_disabled(
        cls: type,
        database: AIOEngine,
        username: str,
    ) -> List['Namespace']:
        username = username.lower()
        return await database.find(
            cls,
            (
                (cls.allowed_users.in_([username]))
            )
        )

    @classmethod
    async def get_allowed(
        cls: 'Namespace',
        database: AIOEngine,
        username: str,
        include_disabled: bool = False,
    ) -> List['Namespace']:
        if include_disabled:
            return await cls.get_multiple_disabled(database, username)
        return await cls.get_multiple(database, username)

    @classmethod
    async def get_disabled(
        cls: type,
        database: AIOEngine,
        username: str
    ) -> List['Namespace']:
        return await cls.get_multiple(database, username, False)

    @classmethod
    async def is_allowed(
        cls: 'Namespace',
        namespace: str,
        database: AIOEngine,
        username: str,
        include_disabled: bool = False,
    ):
        if include_disabled:
            namespaces = await cls.get_multiple_disabled(database, username)
        else:
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
        namespace_in_db = await cls.get(database, namespace, username)
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
        namespaces = await cls.get_multiple(database, username)
        namespace_names = [ns.namespace for ns in namespaces]
        info(f"User {username} has access to {', '.join(namespace_names)}")
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
        namespace: str,
        include_disabled: bool = False
    ) -> List[AsyncIOMotorDatabase]:
        if include_disabled:
            namespaces = await cls.get_multiple_disabled(database, username)
        else:
            namespaces = await cls.get_multiple(database, username)
        if namespaces:
            return [
                await cls.get_namespace_db(
                    database, ns.namespace, username)
                for ns in namespaces if namespace in ["default", "all"] or ns.namespace == namespace  # noqa: E501
            ]
        return []
