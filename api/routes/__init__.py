from fastapi import APIRouter

from .v1 import api as api_v1


api = APIRouter()

# TODO: add all routes here
api.include_router(api_v1, prefix="/v1", tags=["v1"])

__all__ = [api]
