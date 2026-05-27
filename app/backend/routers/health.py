"""Health endpoints."""

from fastapi import APIRouter

from app.backend.config import settings
from app.backend.database import check_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    db_ok = await check_database()
    return {
        "status": "ok",
        "version": settings.app_version,
        "database": "ok" if db_ok else "error",
    }
