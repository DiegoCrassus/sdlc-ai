"""FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.config import settings
from app.backend.database import init_db
from app.backend.errors import register_exception_handlers
from app.backend.routers import assets, health, history, quotes, watchlist


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan, openapi_url="/api/v1/openapi.json")
register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api_v1 = "/api/v1"
app.include_router(health.router, prefix=api_v1)
app.include_router(assets.router, prefix=api_v1)
app.include_router(quotes.router, prefix=api_v1)
app.include_router(history.router, prefix=api_v1)
app.include_router(watchlist.router, prefix=api_v1)


@app.get("/")
async def root() -> dict[str, str]:
    return {"app": settings.app_name, "docs": "/docs"}
