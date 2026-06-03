from __future__ import annotations

from fastapi import APIRouter

from studio_service.api.routes import dashboard, engine, health, readiness, session

router = APIRouter()
router.include_router(health.router)
router.include_router(readiness.router)
router.include_router(session.router)
router.include_router(engine.router)
router.include_router(dashboard.router)
