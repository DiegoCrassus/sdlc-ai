"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.models import HealthResponse
from marketpulse.providers.base import MarketDataProvider

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(provider: MarketDataProvider = Depends(get_market_provider_dep)) -> HealthResponse:
    return HealthResponse(status="ok", provider=provider.provider_name)
