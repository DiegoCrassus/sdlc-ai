"""Projection routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.models import AssetProjection
from marketpulse.providers.base import MarketDataProvider, NotConfiguredError

router = APIRouter(prefix="/projections", tags=["projections"])


@router.get("/{symbol}", response_model=AssetProjection)
async def get_projection(
    symbol: str,
    horizon_days: int = Query(default=7, ge=1, le=90),
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> AssetProjection:
    try:
        return await provider.get_projection(symbol, horizon_days)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NotConfiguredError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
