from pydantic import BaseModel
from pydantic import Field
from typing import Dict
from datetime import datetime


class MongoDBCredentials(BaseModel):
    database: str
    username: str
    password: str
    host: str
    port: int
    url: str
    extra_args: Dict[str, str] = Field(default={})


class RabbitMQCredentials(BaseModel):
    virtual_host: str
    username: str
    password: str
    host: str
    port: int
    url: str


class RedisCredentials(BaseModel):
    key_prefix: str
    username: str
    password: str
    host: str
    port: int
    url: str


class ManagementCredentialsCollection(BaseModel):
    mongodb: MongoDBCredentials = Field()
    rabbitmq: RabbitMQCredentials
    redis: RedisCredentials


class ManagementCredentials(BaseModel):
    namespace: str
    credentials: ManagementCredentialsCollection
    creator: str
    created_at: datetime
