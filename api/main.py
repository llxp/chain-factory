from os import getenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient
from amqpstorm.management import ManagementApi
from aioredis import from_url

from api.auth.models.credentials import Credentials
from api.routes import api
from .auth import api as auth_api
from .constants import default_cors_origins


# environment variables
# --------------------------------
# openssl rand -hex 32
server_secret = getenv(
    "SERVER_SECRET",
    "0d763e4211a42b77e54a2f0a694c1f538bac8479da31a6926024bd445213ceef"
)
postgres_url = getenv(
    "POSTGRES_URL",
    "postgres://postgres:postgres@localhost:5432/postgres"
)
postgres_url = postgres_url.replace('postgres://', 'postgresql+asyncpg://')
mongodb_url = getenv(
    "MONGODB_URL",
    "mongodb://root:example@127.0.0.1:27017/test?authSource=admin"
)
mongodb_database = getenv("MONGODB_DATABASE", "test")
redis_url = getenv("REDIS_URL", "redis://localhost")
translate_users_username = getenv("IDP_USERNAME", "llxp@jumpcloud.com")
translate_users_password = getenv("IDP_PASSWORD", "WmNNJPf7wTurU9t")
rabbitmq_management_host = getenv(
    "RABBITMQ_MANAGEMENT_HOST", "127.0.0.1")
rabbitmq_management_user = getenv("RABBITMQ_MANAGEMENT_USER", "guest")
rabbitmq_management_pass = getenv("RABBITMQ_MANAGEMENT_PASS", "guest")
rabbitmq_management_port = getenv("RABBITMQ_MANAGEMENT_PORT", 15672)
rabbitmq_url = getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
origins = getenv("DEFAULT_CORS_ORIGINS", default_cors_origins)
# --------------------------------

# initialize fastapi
app = FastAPI()
app.include_router(auth_api, prefix="/auth")
app.include_router(api, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize rabbitmq management api
rabbitmq_management_url = getenv(
    "RABBITMQ_MANAGEMENT_URL",
    f'http://{rabbitmq_management_host}:{rabbitmq_management_port}'
)
rabbitmq_management_api = ManagementApi(
    api_url=rabbitmq_management_url,
    username=rabbitmq_management_user,
    password=rabbitmq_management_pass,
    verify=False
)

# initialize database connection
motor_client = AsyncIOMotorClient(mongodb_url)
odm_session = AIOEngine(motor_client=motor_client, database=mongodb_database)

# initialize redis client
redis_client = from_url(redis_url)


@app.middleware("http")
async def set_request_parameter(request: Request, call_next):
    # TODO: place additional global variables here
    # to make them available during a request
    # e.g. request.db_session = db_session
    request.state.server_secret = server_secret
    request.state.odm_session = odm_session
    request.state.idp_credentials = Credentials(
        username=translate_users_username,
        password=translate_users_password
    )
    request.state.redis_client = redis_client
    request.state.rabbitmq_management_api = rabbitmq_management_api
    request.state.rabbitmq_url = rabbitmq_url
    return await call_next(request)
