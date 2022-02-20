from http.client import HTTPException
from fastapi import Request


async def get_server_secret(request: Request):
    try:
        return request.state.server_secret
    except AttributeError:
        return None


async def get_odm_session(request: Request):
    try:
        return request.state.odm_session
    except AttributeError:
        raise HTTPException(status_code=500, detail='ODM session not set')


async def get_idp_credentials(request: Request):
    try:
        return request.state.idp_credentials
    except AttributeError:
        return None


async def get_username(request: Request):
    try:
        return request.state.username
    except AttributeError:
        return None


async def get_hostname(request: Request):
    try:
        return request.url.hostname
    except AttributeError:
        return None
