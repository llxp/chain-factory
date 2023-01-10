from json import dumps
from typing import Union

from requests import post, get, Response

from .models.credentials import ManagementCredentials


class CredentialsRetriever():
    """
    Retrieve database credentials from rest api
    """

    def __init__(
        self,
        endpoint: str,
        namespace: str,
        username: str,
        password: str,
        key: str
    ):
        self.endpoint = endpoint
        self.namespace = namespace
        self.username = username
        self.password = password
        self.mongodb_host = "localhost"
        self.mongodb_port = 27017
        self.headers = dict(
            Accept="application/json",
            ContentType="application/json"
        )
        self.access_token = None
        self.extra_arguments = dict(authSource="admin")
        self.key = key
        self.credentials: Union[ManagementCredentials, None] = None
        self.jwe_token = None

    async def init(self):
        """
        The init method is used to initialize the class
        as the `__init__` method does not work with async
        """
        self.jwe_token = self.get_jwe_token(self.username, self.password)
        if (
            isinstance(self.jwe_token, dict) and
            "access_token" in self.jwe_token and "token" in self.jwe_token["access_token"]  # noqa: E501
        ):
            self.credentials = self.get_credentials()
            if self.credentials is None:
                raise Exception("Credentials not found")
        else:
            raise Exception("Token not valid")

    @property
    def mongodb(self) -> str:
        """get MongoDB credentials from credentials"""
        if self.credentials is None:
            raise Exception("Credentials not found")
        return self.credentials.credentials.mongodb.url

    @property
    def redis(self) -> str:
        """get redis credentials from credentials"""
        if self.credentials is None:
            raise Exception("Credentials not found")
        return self.credentials.credentials.redis.url

    @property
    def redis_prefix(self) -> str:
        """get redis prefix from credentials"""
        if self.credentials is None:
            raise Exception("Credentials not found")
        return self.credentials.credentials.redis.key_prefix

    @property
    def rabbitmq(self) -> str:
        """get rabbitmq credentials from credentials"""
        if self.credentials is None:
            raise Exception("Credentials not found")
        return self.credentials.credentials.rabbitmq.url

    def get_jwe_token(self, username, password) -> Union[dict, None]:
        """send login request to internal rest-api on /api/login"""
        response: Response = post(
            url=self.endpoint + "/auth/login",
            data=dumps({
                "username": username,
                "password": password,
                "scopes": ["user"]
            }),
            headers=self.headers
        )
        # get jwe token from response
        if response.status_code == 200:
            return response.json()
        return None

    def get_credentials(self) -> Union[ManagementCredentials, None]:
        """
        retrieve namespace credentials
        from internal rest-api on /api/v1/credentials
        using login token and namespace/namespace-key
        (which is used to decrypt the credentials
        created on namespace key rotation)
        """
        if self.jwe_token is None:
            raise Exception("Token not valid")
        token = self.jwe_token["access_token"]["token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # send request to /api/v1/credentials
        response = get(url=f"{self.endpoint}/api/v1/namespaces/{self.namespace}/credentials?key={self.key}", headers=headers)  # noqa: E501
        if response.status_code == 200:
            # get credentials from response
            return ManagementCredentials(**response.json())
        return None
