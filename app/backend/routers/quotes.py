"""Quote routes."""

from fastapi import APIRouter, Query

from app.backend.errors import AppError
from app.backend.schemas import BatchQuotes, Quote
from app.backend.services import market_data
from app.backend.utils.asset_id import parse_asset_id

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("", response_model=BatchQuotes)
async def batch_quotes(ids: str = Query(..., min_length=1)) -> BatchQuotes:
    asset_ids = [part.strip() for part in ids.split(",") if part.strip()]
    if not asset_ids:
        raise AppError("VALIDATION_ERROR", "At least one asset ID is required")
    return await market_data.get_quotes(asset_ids)


@router.get("/{asset_id:path}", response_model=Quote)
async def get_quote(asset_id: str) -> Quote:
    try:
        parse_asset_id(asset_id)
    except Exception as exc:
        raise AppError("VALIDATION_ERROR", str(exc)) from exc
    return await market_data.get_quote(asset_id)
