"""API v1 router."""

from fastapi import APIRouter

from marketpulse.api.v1.routes import health, markets, projections, watchlist

router = APIRouter()
router.include_router(health.router)
router.include_router(markets.router)
router.include_router(projections.router)
router.include_router(watchlist.router)
