from logging import debug
# , getLogger, Formatter, basicConfig
# from logging.handlers import SysLogHandler
from os import getenv

# Import FastAPI for Rest API, Swagger Docs
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.openapi.utils import get_openapi

# ODM: Object Document Mapper to serialize classes into MongoDB Objects
from odmantic import AIOEngine

# odmantic uses motor
from motor.motor_asyncio import AsyncIOMotorClient

# Accesses ManagementAPI Redis
from amqpstorm.management import ManagementApi

from api.auth.models.credentials import Credentials
from api.routes import api
from .auth import api as auth_api

# environment variables
# --------------------------------

# Server secret to sign access tokens (openssl rand -hex 32)
server_secret = getenv(
    "SERVER_SECRET",
    "0d763e4211a42b77e54a2f0a694c1f538bac8479da31a6926024bd445213ceef"
)

# MongoDB details
mongodb_url = getenv(
    "MONGODB_URL",
    "mongodb://root:example@127.0.0.1:27017/db?authSource=admin"
)
mongodb_database = getenv("MONGODB_DATABASE", "db")

# Redis details
redis_url = getenv("REDIS_URL", "redis://localhost")

# Service account for fetching user details from the Active Directory
translate_users_username = getenv("IDP_USERNAME", "llxp@jumpcloud.com")
translate_users_password = getenv("IDP_PASSWORD", "WmNNJPf7wTurU9t")

# RabbitMQ details
rabbitmq_management_host = getenv("RABBITMQ_MANAGEMENT_HOST", "127.0.0.1")
rabbitmq_management_user = getenv("RABBITMQ_MANAGEMENT_USER", "guest")
rabbitmq_management_pass = getenv("RABBITMQ_MANAGEMENT_PASS", "guest")
rabbitmq_manangement_verify = getenv("RABBITMQ_MANAGEMENT_VERIFY", "false")
rabbitmq_management_port = getenv("RABBITMQ_MANAGEMENT_PORT", 8002)
rabbitmq_url = getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

default_origins = getenv("DEFAULT_CORS_ORIGINS")
origins = default_origins.split(",") if default_origins else []  # noqa: E501
print(f"origins {origins}")

# Local admin user account as fallback for WebUI access
breakglass_username = getenv("BREAKGLASS_USERNAME", "breakglass")
breakglass_domain = getenv("BREAKGLASS_DOMAIN", "breakglass")
bg_username_lower = breakglass_username.lower()
bg_domain_lower = breakglass_domain.lower()

# Initialize FastAPI
app = FastAPI(docs_url=None, redoc_url=None)
app.include_router(auth_api, prefix="/auth")
app.include_router(api, prefix="/api")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Origin", "X-Requested-With", "Content-Type", "Accept", "Authorization", "Cookies"],  # noqa: E501
)
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if app.openapi_url is None:
        raise Exception("openapi_url is not set")
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    )


@app.get(app.swagger_ui_oauth2_redirect_url or "", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    if app.openapi_url is None:
        raise Exception("openapi_url is not set")
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png",
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Chain Factory API",
        version="1.0.0",
        description="API for Chain Factory",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Initialize RabbitMQ management api
default = f"http://{rabbitmq_management_host}:{rabbitmq_management_port}"
debug(f"default rabbitmq management api: {default}")
rabbitmq_management_url = getenv("RABBITMQ_MANAGEMENT_URL")
if not rabbitmq_management_url:
    rabbitmq_management_url = default

# debug(f"rabbitmq_management_url: {rabbitmq_management_url}")
# debug(f"rabbitmq_management_user: {rabbitmq_management_user}")
# debug(f"rabbitmq_management_pass: {rabbitmq_management_pass}")
rabbitmq_management_api = ManagementApi(
    api_url=rabbitmq_management_url,
    username=rabbitmq_management_user,
    password=rabbitmq_management_pass,
    verify=rabbitmq_manangement_verify if len(rabbitmq_manangement_verify) > 0 else False,  # noqa: E501
)

# Initialize MongoDB connection
motor_client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, socketTimeoutMS=3000)  # noqa: E501
odm_session = AIOEngine(motor_client=motor_client, database=mongodb_database)


@app.middleware("http")
async def set_request_parameter(request: Request, call_next):
    # TODO: place additional global variables here
    # to make them available during a request
    # e.g. request.db_session = db_session
    request.state.breakglass_username = bg_username_lower
    request.state.breakglass_domain = bg_domain_lower
    request.state.server_secret = server_secret
    request.state.odm_session = odm_session
    request.state.idp_credentials = Credentials(
        username=translate_users_username, password=translate_users_password)
    request.state.redis_url = redis_url
    request.state.rabbitmq_management_api = rabbitmq_management_api
    request.state.rabbitmq_url = rabbitmq_url
    return await call_next(request)


@app.get("/")
@app.get("/health")
async def health():
    debug("health check")
    return {"status": "ok"}
