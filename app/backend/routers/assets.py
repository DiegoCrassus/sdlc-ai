"""Asset routes."""

from fastapi import APIRouter, HTTPException, Query

from app.backend.schemas import (
    AssetDetail,
    AssetSearchResult,
    AssetType,
    HistoryRange,
    PriceHistory,
)
from app.backend.services import market_data

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/search", response_model=list[AssetSearchResult])
async def search(q: str = "", limit: int = Query(20, ge=1, le=50)):
    return await market_data.search_assets(q, limit)


@router.get("/{symbol}", response_model=AssetDetail)
async def detail(symbol: str, asset_type: AssetType = Query(...)):
    return await market_data.get_asset_detail(symbol, asset_type)


@router.get("/{symbol}/history", response_model=PriceHistory)
async def history(symbol: str, asset_type: AssetType = Query(...), range: HistoryRange = Query("7d")):
    h = await market_data.get_price_history(symbol, asset_type, range)
    if not h.points:
        raise HTTPException(404, "No history")
    return h
