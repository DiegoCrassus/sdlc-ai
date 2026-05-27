"""Asset discovery routes."""

from fastapi import APIRouter, Query

from app.backend.errors import AppError
from app.backend.schemas import Asset, AssetClass, PaginatedAssets
from app.backend.services import market_data
from app.backend.utils.asset_id import parse_asset_id

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/search", response_model=PaginatedAssets)
async def search(
    q: str = Query(..., min_length=1),
    asset_class: AssetClass | None = Query(None, alias="class"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> PaginatedAssets:
    return await market_data.search_assets(q, limit=limit, offset=offset, asset_class=asset_class)


@router.get("/{asset_id:path}", response_model=Asset)
async def get_asset(asset_id: str) -> Asset:
    try:
        parse_asset_id(asset_id)
    except Exception as exc:
        raise AppError("VALIDATION_ERROR", str(exc)) from exc
    return await market_data.get_asset(asset_id)
