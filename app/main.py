from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.scheduler import (
    start_scheduler,
    refresh_kite_token
)

import logging

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

    # Generate token immediately
    refresh_kite_token()

    # Schedule daily refresh
    start_scheduler()