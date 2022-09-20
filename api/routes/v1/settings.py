from os import getenv

default_mongodb_host: str = getenv("MONGODB_HOST", '127.0.0.1')
default_mongodb_port: int = int(getenv("MONGODB_PORT", 27017))
default_mongodb_extra_args: dict = getenv("MONGODB_EXTRA_ARGS", "").split("&")
default_redis_host = getenv("REDIS_HOST", '127.0.0.1')
default_redis_port = int(getenv("REDIS_PORT", 6379))
default_rabbitmq_host = getenv("RABBITMQ_HOST", '127.0.0.1')
default_rabbitmq_port = int(getenv("RABBITMQ_PORT", 5672))
