"""Watchlist persistence and enrichment."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.errors import AppError
from app.backend.models import WatchlistItemRow
from app.backend.schemas import (
    PaginatedWatchlist,
    WatchlistItem,
    WatchlistItemCreate,
    WatchlistItemUpdate,
)
from app.backend.services import market_data


def _row_to_item(row: WatchlistItemRow) -> WatchlistItem:
    return WatchlistItem(
        asset_id=row.asset_id,
        notes=row.notes,
        sort_order=row.sort_order,
        added_at=row.added_at,
    )


async def list_watchlist(
    session: AsyncSession,
    *,
    limit: int = 20,
    offset: int = 0,
    embed_market_data: bool = True,
) -> PaginatedWatchlist:
    total_result = await session.execute(select(func.count()).select_from(WatchlistItemRow))
    total = int(total_result.scalar_one())

    result = await session.execute(
        select(WatchlistItemRow)
        .order_by(WatchlistItemRow.sort_order, WatchlistItemRow.added_at)
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()

    items: list[WatchlistItem] = []
    for row in rows:
        item = _row_to_item(row)
        if embed_market_data:
            try:
                item.asset = await market_data.get_asset(row.asset_id)
                item.quote = await market_data.get_quote(row.asset_id)
            except AppError:
                pass
        items.append(item)

    return PaginatedWatchlist(items=items, total=total, limit=limit, offset=offset)


async def add_watchlist_item(
    session: AsyncSession,
    body: WatchlistItemCreate,
) -> tuple[WatchlistItem, bool]:
    """Add item. Returns (item, created) where created=False means duplicate."""
    try:
        await market_data.get_asset(body.asset_id)
    except AppError as exc:
        if exc.code == "NOT_FOUND":
            raise
        raise

    existing = await session.get(WatchlistItemRow, body.asset_id)
    if existing:
        return _row_to_item(existing), False

    row = WatchlistItemRow(
        asset_id=body.asset_id,
        notes=body.notes,
        sort_order=body.sort_order,
        added_at=datetime.now(UTC),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _row_to_item(row), True


async def update_watchlist_item(
    session: AsyncSession,
    asset_id: str,
    body: WatchlistItemUpdate,
) -> WatchlistItem:
    row = await session.get(WatchlistItemRow, asset_id)
    if not row:
        raise AppError("NOT_FOUND", f"Watchlist item not found: {asset_id}", status_code=404)

    if body.notes is not None:
        row.notes = body.notes
    if body.sort_order is not None:
        row.sort_order = body.sort_order

    await session.commit()
    await session.refresh(row)
    return _row_to_item(row)


async def delete_watchlist_item(session: AsyncSession, asset_id: str) -> None:
    row = await session.get(WatchlistItemRow, asset_id)
    if not row:
        raise AppError("NOT_FOUND", f"Watchlist item not found: {asset_id}", status_code=404)
    await session.delete(row)
    await session.commit()
