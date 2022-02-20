from typing import List
from pydantic import BaseModel
from odmantic import AIOEngine, Model

from ....auth.utils.credentials import get_domain


class Namespace(Model):
    namespace: str = ""
    domain: str = ""
    enabled: bool = True
    allowed_users: List[str]  # list of user ids

    @classmethod
    async def get_multiple(
        cls: type,
        database: AIOEngine,
        domain: str,
        username: str
    ) -> List['Namespace']:
        if domain:
            return await database.find(
                cls,
                (
                    (cls.enabled == True) &  # noqa: E712
                    (cls.domain == domain) &
                    (cls.allowed_users.in_([username]))
                )
            )
        return None

    @classmethod
    async def is_allowed(
        cls: type,
        namespace: str,
        database: AIOEngine,
        username: str
    ):
        domain = await get_domain(username)
        print(database, domain, username)
        namespaces = await cls.get_multiple(database, domain, username)
        if namespaces:
            namespaces = [
                ns for ns in namespaces if ns.namespace == namespace]
            return len(namespaces) > 0
        return False


class NamespaceCreatedResponse(BaseModel):
    namespace: str = ""
