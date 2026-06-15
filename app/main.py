from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.scheduler import (
    start_scheduler,
    refresh_kite_token
)

from app.api.v1.api import api_router

app = FastAPI(
    title="Spread Strategy API",
    version="1.0.0"
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.on_event("startup")
def startup_event():
    logger.warning("STARTUP EVENT EXECUTED")

    if refresh_kite_token():
        logger.info("TOKEN REFRESH COMPLETE")
    else:
        logger.error("TOKEN REFRESH FAILED")

    start_scheduler()

    logger.warning("SCHEDULER STARTED")