from logging import info
from typing import Dict

# direct imports
from .credentials_retriever import CredentialsRetriever


class CredentialsPool:
    """
    CredentialsPool is a class that is responsible for managing the
    database credentials for a specific namespace. Can be retrieved
    using the credentials and the namespace key.
    """

    def __init__(
        self,
        endpoint: str,
        username: str,
        password: str,
        namespaces: Dict[str, str] = {}
    ):
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.namespaces = namespaces
        self._credentials: Dict[str, CredentialsRetriever] = {}

    async def init(self):
        for namespace in self.namespaces:
            info(f"Initialising credentials for {namespace}")
            await self.get_credentials(namespace, self.namespaces[namespace])

    async def get_credentials(
        self,
        namespace: str,
        key: str = ""
    ) -> CredentialsRetriever:
        """
        Get the credentials for the namespace.
        """
        try:
            return self._credentials[namespace]
        except KeyError:
            if key == "":
                raise Exception("Trying to get credentials for yet unknown namespace without a key. Please request the credentials during initialization of the worker node.")  # noqa: E501
            self._credentials[namespace] = CredentialsRetriever(self.endpoint, namespace, self.username, self.password, key)  # noqa: E501
            await self._credentials[namespace].init()
            return self._credentials[namespace]

    async def update_credentials(self):
        """
        Update the credentials internally for the namespace.
        """
        namespaces = self._credentials.keys()
        self._credentials = {}
        for namespace in namespaces:
            await self.get_credentials(namespace, self.namespaces[namespace])
