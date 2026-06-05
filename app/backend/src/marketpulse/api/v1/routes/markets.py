"""Market data routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.enums import Interval
from marketpulse.domain.models import (
    CompareResponse,
    MarketOverview,
    PriceHistory,
    Quote,
    SearchHit,
)
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services.compare import (
    InsufficientAlignedDataError,
    build_compare_response,
    parse_compare_symbols,
)

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


@router.get("/compare", response_model=CompareResponse)
async def markets_compare(
    symbols: str = Query(..., description="Comma-separated symbols, 2-4 unique"),
    days: int = Query(default=90, ge=7, le=365),
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> CompareResponse:
    parsed = parse_compare_symbols(symbols)
    if len(parsed) < 2 or len(parsed) > 4:
        raise HTTPException(status_code=422, detail="invalid_symbol_count")
    try:
        return await build_compare_response(provider, parsed, days)
    except InsufficientAlignedDataError as exc:
        raise HTTPException(status_code=422, detail="insufficient_aligned_data") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
