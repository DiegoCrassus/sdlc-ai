"""Market data REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.backend.src.api.deps import MarketProviderDep
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    CurrentPrice,
    HistoricalPrices,
    MarketSummary,
    PriceInterval,
    PriceRange,
    ProviderHealth,
)

router = APIRouter(prefix="/api/v1/market", tags=["market-data"])


@router.get("/search", response_model=list[AssetSearchResult])
async def search_assets(
    provider: MarketProviderDep,
    q: str = Query(..., min_length=1, description="Search query"),
    asset_type: AssetType | None = Query(None, alias="asset_type"),
) -> list[AssetSearchResult]:
    return await provider.search_assets(q, asset_type)


@router.get("/price/{symbol}", response_model=CurrentPrice)
async def get_current_price(
    symbol: str,
    provider: MarketProviderDep,
    asset_type: AssetType = Query(..., alias="asset_type"),
) -> CurrentPrice:
    price = await provider.get_current_price(symbol, asset_type)
    if price is None:
        raise HTTPException(status_code=404, detail=f"No price found for {symbol}")
    return price


@router.get("/history/{symbol}", response_model=HistoricalPrices)
async def get_historical_prices(
    symbol: str,
    provider: MarketProviderDep,
    asset_type: AssetType = Query(..., alias="asset_type"),
    range: PriceRange = Query(PriceRange.MONTH, alias="range"),
    interval: PriceInterval = Query(PriceInterval.DAY, alias="interval"),
) -> HistoricalPrices:
    history = await provider.get_historical_prices(symbol, asset_type, range, interval)
    if history is None:
        raise HTTPException(status_code=404, detail=f"No history found for {symbol}")
    return history


@router.get("/metadata/{symbol}", response_model=AssetMetadata)
async def get_asset_metadata(
    symbol: str,
    provider: MarketProviderDep,
    asset_type: AssetType = Query(..., alias="asset_type"),
) -> AssetMetadata:
    metadata = await provider.get_asset_metadata(symbol, asset_type)
    if metadata is None:
        raise HTTPException(status_code=404, detail=f"No metadata found for {symbol}")
    return metadata


@router.get("/summary", response_model=MarketSummary)
async def get_market_summary(provider: MarketProviderDep) -> MarketSummary:
    summary = await provider.get_market_summary()
    if summary is None:
        raise HTTPException(status_code=503, detail="Market summary unavailable")
    return summary


@router.get("/providers/health", response_model=ProviderHealth)
async def get_provider_health(provider: MarketProviderDep) -> ProviderHealth:
    return await provider.get_provider_health()
