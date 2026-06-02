from fastapi import APIRouter

from app.api.v1.routes import auth
from app.api.v1.routes import health
from app.api.v1.routes import market

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

api_router.include_router(
    market.router,
    prefix="/market",
    tags=["Market"]
)