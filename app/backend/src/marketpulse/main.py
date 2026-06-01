"""MarketPulse FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from marketpulse.api.errors import register_alert_exception_handler
from marketpulse.api.v1.router import router as api_v1_router
from marketpulse.config import get_settings
from marketpulse.db import dispose_engine, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await dispose_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_alert_exception_handler(app)
    app.include_router(api_v1_router, prefix=settings.api_prefix)
    return app


app = create_app()
