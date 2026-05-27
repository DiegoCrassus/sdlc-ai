"""Watchlist routes."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.database import get_db
from app.backend.errors import AppError
from app.backend.schemas import (
    PaginatedWatchlist,
    WatchlistItem,
    WatchlistItemCreate,
    WatchlistItemUpdate,
)
from app.backend.services import watchlist as watchlist_service
from app.backend.utils.asset_id import format_asset_id, parse_asset_id

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _normalize_asset_id(asset_id: str) -> str:
    try:
        asset_class, symbol = parse_asset_id(asset_id)
    except Exception as exc:
        raise AppError("VALIDATION_ERROR", str(exc)) from exc
    return format_asset_id(asset_class, symbol)


@router.get("", response_model=PaginatedWatchlist)
async def list_watchlist(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
) -> PaginatedWatchlist:
    return await watchlist_service.list_watchlist(session, limit=limit, offset=offset)


@router.post("/items", response_model=WatchlistItem)
async def add_watchlist_item(
    body: WatchlistItemCreate,
    response: Response,
    session: AsyncSession = Depends(get_db),
) -> WatchlistItem:
    normalized = _normalize_asset_id(body.asset_id)
    payload = body.model_copy(update={"asset_id": normalized})
    item, created = await watchlist_service.add_watchlist_item(session, payload)
    response.status_code = 201 if created else 200
    return item


@router.patch("/items/{asset_id:path}", response_model=WatchlistItem)
async def update_watchlist_item(
    asset_id: str,
    body: WatchlistItemUpdate,
    session: AsyncSession = Depends(get_db),
) -> WatchlistItem:
    normalized = _normalize_asset_id(asset_id)
    return await watchlist_service.update_watchlist_item(session, normalized, body)


@router.delete("/items/{asset_id:path}", status_code=204)
async def delete_watchlist_item(
    asset_id: str,
    session: AsyncSession = Depends(get_db),
) -> Response:
    normalized = _normalize_asset_id(asset_id)
    await watchlist_service.delete_watchlist_item(session, normalized)
    return Response(status_code=204)
