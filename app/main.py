from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.scheduler import (
    start_scheduler,
    refresh_kite_token
)

from app.api.v1.api import api_router

app = FastAPI(
    title="Spread Strategy API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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