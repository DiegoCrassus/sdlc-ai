"""Market data routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.enums import Interval
from marketpulse.domain.models import MarketOverview, PriceHistory, Quote, SearchHit
from marketpulse.providers.base import MarketDataProvider

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("/overview", response_model=MarketOverview)
async def markets_overview(
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> MarketOverview:
    return await provider.get_overview()


@router.get("/quotes", response_model=list[Quote])
async def markets_quotes(
    symbols: str = Query(..., description="Comma-separated symbols, e.g. AAPL,BTC"),
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> list[Quote]:
    quotes: list[Quote] = []
    for raw_symbol in symbols.split(","):
        symbol = raw_symbol.strip()
        if not symbol:
            continue
        try:
            quotes.append(await provider.get_quote(symbol))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    return quotes


@router.get("/search", response_model=list[SearchHit])
async def markets_search(
    q: str = Query(..., min_length=1),
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> list[SearchHit]:
    return await provider.search(q)


@router.get("/{symbol}/ohlcv", response_model=PriceHistory)
async def markets_ohlcv(
    symbol: str,
    interval: Interval = Interval.DAY_1,
    limit: int = Query(default=90, ge=1, le=365),
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> PriceHistory:
    try:
        return await provider.get_ohlcv(symbol, interval, limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
