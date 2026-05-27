"""Price history routes."""

from datetime import date

from fastapi import APIRouter, Query

from app.backend.errors import AppError
from app.backend.schemas import HistoryInterval, HistoryResponse
from app.backend.services import market_data
from app.backend.utils.asset_id import parse_asset_id

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/{asset_id:path}", response_model=HistoryResponse)
async def get_history(
    asset_id: str,
    interval: HistoryInterval = Query("1d"),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
) -> HistoryResponse:
    try:
        parse_asset_id(asset_id)
    except Exception as exc:
        raise AppError("VALIDATION_ERROR", str(exc)) from exc
    return await market_data.get_history(asset_id, interval=interval, from_date=from_date, to_date=to_date)
