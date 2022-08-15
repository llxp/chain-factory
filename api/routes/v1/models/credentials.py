from http.client import HTTPException
from logging import error, info, warning
from typing import Union
from datetime import datetime
# from aioredis import Redis
from redis import Redis
from cryptography.fernet import Fernet
from amqpstorm.management import ManagementApi, ApiError
from traceback import print_exc
from odmantic import AIOEngine, EmbeddedModel, Field, Model
from pydantic import BaseModel
from pymongo.errors import OperationFailure

from ..utils import encrypt


class MongoDBCredentials(EmbeddedModel):
    database: str
    username: str
    password: str
    host: str
    port: int
    url: str

    @classmethod
    async def new(
        cls: type,
        database: AIOEngine,
        namespace: str,
        domain: str,
        email: str,
        host: str,
        port: int,
    ) -> 'MongoDBCredentials':
        # create mongodb credentials in the server
        # allow the user to access the namespace
        domain_snake_case = domain.replace('.', '_')
        email_snake_case = email.replace('.', '_').replace('@', '_')
        # alphabet = string.ascii_letters + string.digits
        # rnd = ''.join(secrets.choice(alphabet) for i in range(5))
        password = Fernet.generate_key().decode('utf-8')
        username = email_snake_case + '_' + namespace
        db_name = namespace + '_' + domain_snake_case
        try:
            await database.client[db_name].command(
                'createUser',
                username,
                roles=[
                    'readWrite',
                    'dbAdmin'
                ],
                pwd=password
            )
        except OperationFailure as e:
            if e.code == 51003:
                warning("user already exists")
                # update user
                await database.client[db_name].command(
                    'updateUser',
                    username,
                    roles=[
                        'readWrite',
                        'dbAdmin'
                    ],
                    pwd=password
                )
            else:
                error(e.code)
                print_exc()
        except Exception as e:
            print_exc()
            error(e)
            return None
        return cls(
            database=db_name,
            username=username,
            password=password,
            host=host,
            port=port,
            url=f'mongodb://{username}:{password}@{host}:{port}/{db_name}?readPreference=primaryPreferred'  # noqa: E501
        )


class RabbitMQCredentials(EmbeddedModel):
    virtual_host: str
    username: str
    password: str
    host: str
    port: int
    url: str

    @classmethod
    async def new(
        cls: type,
        client: ManagementApi,
        namespace: str,
        domain: str,
        email: str,
        host: str,
        port: int
    ) -> 'RabbitMQCredentials':
        # create rabbitmq credentials in the server
        # allow the user to access the namespace
        domain_snake_case = domain.replace('.', '_')
        email_snake_case = email.replace('.', '_').replace('@', '_')
        # alphabet = string.ascii_letters + string.digits
        # rnd = ''.join(secrets.choice(alphabet) for i in range(5))
        password = Fernet.generate_key().decode('utf-8')
        username = email_snake_case + '_' + namespace
        vhost_name = namespace + '_' + domain_snake_case
        try:
            result_create_vhost = client.virtual_host.create(vhost_name)
            info(result_create_vhost)
            result_create_user = client.user.create(
                username=username,
                password=password,
                tags='management'
            )
            info(result_create_user)
            result_set_permission = client.user.set_permission(
                username=username,
                virtual_host=vhost_name,
                configure_regex='.*',
                write_regex='.*',
                read_regex='.*'
            )
            info(result_set_permission)
        except ApiError:
            print_exc()
        except Exception as e:
            print_exc()
            error(e)
            return None

        return cls(
            virtual_host=vhost_name,
            username=username,
            password=password,
            host=host,
            port=port,
            url=f"amqp://{username}:{password}@{host}:{port}/{vhost_name}",
        )


class RedisCredentials(EmbeddedModel):
    key_prefix: str
    username: str
    password: str
    host: str
    port: int
    url: str

    @classmethod
    async def new(
        cls: type,
        client: Redis,
        namespace: str,
        domain: str,
        email: str,
        host: str,
        port: int
    ) -> 'RedisCredentials':
        # create redis credentials in the server
        # allow the user to access the namespace
        domain_snake_case = domain.replace('.', '_')
        email_snake_case = email.replace('.', '_').replace('@', '_')
        # alphabet = string.ascii_letters + string.digits
        # rnd = ''.join(secrets.choice(alphabet) for i in range(5))
        password = Fernet.generate_key().decode('utf-8')
        username = email_snake_case + '_' + namespace
        db_name = namespace + '_' + domain_snake_case
        # set acl for the namespace
        if not client.acl_setuser(
            username=username,
            enabled=True,
            keys=[db_name + '_*'],
            passwords='+'+password,
            reset_passwords=False,
            reset=True,
            channels=['*'],
            commands=[
                '+set',
                '+get',
                '+subscribe',
                '+unsubscribe',
                '+publish',
            ],
        ):
            raise HTTPException("failed to set redis acl")
        return cls(
            key_prefix=db_name,
            username=username,
            password=password,
            host=host,
            port=port,
            url=f"redis://{username}:{password}@{host}:{port}",
        )


class ManagementCredentialsCollection(EmbeddedModel):
    mongodb: MongoDBCredentials = Field()
    rabbitmq: RabbitMQCredentials
    redis: RedisCredentials

    @classmethod
    async def new(
        cls: type,
        database: AIOEngine,
        rabbitmq_management_client: ManagementApi,
        redis_client: Redis,
        namespace: str,
        domain: str,
        email: str,
        mongodb_host: str,
        mongodb_port: int,
        rabbitmq_host: str,
        rabbitmq_port: int,
        redis_host: str,
        redis_port: int,
    ) -> 'ManagementCredentialsCollection':
        mongodb = await MongoDBCredentials.new(
            database, namespace, domain, email, mongodb_host, mongodb_port
        )
        rabbitmq = await RabbitMQCredentials.new(
            rabbitmq_management_client,
            namespace,
            domain,
            email,
            rabbitmq_host,
            rabbitmq_port
        )
        redis = await RedisCredentials.new(
            redis_client, namespace, domain, email, redis_host, redis_port
        )
        return cls(
            mongodb=mongodb,
            rabbitmq=rabbitmq,
            redis=redis,
        )


class ManagementCredentials(Model):
    namespace: str
    credentials: Union[str, ManagementCredentialsCollection]
    creator: str
    created_at: datetime

    @classmethod
    async def new(
        cls: type['ManagementCredentials'],
        database: AIOEngine,
        rabbitmq_management_client: ManagementApi,
        redis_client: Redis,
        namespace: str,
        domain: str,
        email: str,
        mongodb_host: str,
        mongodb_port: int,
        rabbitmq_host: str,
        rabbitmq_port: int,
        redis_host: str,
        redis_port: int,
    ) -> 'ManagementCredentials':
        credentials_collection = await ManagementCredentialsCollection.new(
            database,
            rabbitmq_management_client,
            redis_client,
            namespace,
            domain,
            email,
            mongodb_host,
            mongodb_port,
            rabbitmq_host,
            rabbitmq_port,
            redis_host,
            redis_port,
        )
        if (
            credentials_collection.mongodb and
            credentials_collection.rabbitmq and
            credentials_collection.redis
        ):
            email_lower = email.lower()
            now = datetime.utcnow()
            credentials_data = cls(
                namespace=namespace,
                credentials=credentials_collection,
                creator=email_lower,
                created_at=now,
            )
            key = Fernet.generate_key()
            credentials_json = credentials_data.credentials.json()
            key_str = key.decode('utf-8')
            encrypted_credentials_data = encrypt(credentials_json, key_str)
            credentials_data.credentials = encrypted_credentials_data
            await database.save(credentials_data)
            return key_str
        return None

    @classmethod
    async def get(
        cls: type['ManagementCredentials'],
        database: AIOEngine,
        namespace: str,
    ) -> 'ManagementCredentials':
        return await database.find_one(ManagementCredentials, (
            (cls.namespace == namespace)
        ))

    @classmethod
    async def delete_one(
        cls: type['ManagementCredentials'],
        database: AIOEngine,
        namespace: str,
        domain: str
    ):
        instance = await cls.get(database, namespace)
        return await database.delete(instance)


class ManagementCredentialsResponse(BaseModel):
    namespace: str
    credentials: ManagementCredentialsCollection
    created_at: datetime
    creator: str
