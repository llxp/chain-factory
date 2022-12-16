from json import dumps

from requests import post, get

from api.routes.v1.models.credentials import ManagementCredentials


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
        self.extra_arguments = dict(authSource="admin")
        self.key = key
        self.credentials = None

    async def init(self):
        self.jwe_token = self.get_jwe_token(self.username, self.password)
        if (
            self.jwe_token and
            isinstance(self.jwe_token, dict) and
            "access_token" in self.jwe_token
        ):
            self.credentials = self.get_credentials()
            if self.credentials is None:
                raise Exception("Credentials not found")
        else:
            raise Exception("Token not valid")

    @property
    def mongodb(self) -> str:
        # get db credentials from credentials
        return self.credentials.credentials.mongodb.url

    @property
    def redis(self) -> str:
        # get redis credentials from credentials
        return self.credentials.credentials.redis.url

    @property
    def redis_prefix(self) -> str:
        # get redis prefix from credentials
        return self.credentials.credentials.redis.key_prefix

    @property
    def rabbitmq(self) -> str:
        # get rabbitmq credentials from credentials
        return self.credentials.credentials.rabbitmq.url

    def get_jwe_token(self, username, password):
        # send login request to /api/login
        response = post(
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

    def get_credentials(self) -> ManagementCredentials:
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
