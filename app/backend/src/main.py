"""FastAPI application entrypoint."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.src.api.routes import health, market_data
from app.backend.src.market_data.factory import build_market_data_provider


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _load_dotenv()
    app.state.market_provider = await build_market_data_provider()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="SDLC Invest API",
        description="Investment platform backend — market data and portfolio services",
        version="0.1.0",
        lifespan=lifespan,
    )
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(market_data.router)
    return app


app = create_app()
