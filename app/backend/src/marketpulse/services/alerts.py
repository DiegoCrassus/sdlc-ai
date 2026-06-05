"""Price alert persistence and trigger evaluation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.db.models import PriceAlertRow
from marketpulse.domain.enums import AlertDirection
from marketpulse.domain.models import CreateAlertRequest, PriceAlert
from marketpulse.providers.base import MarketDataProvider


def _row_to_model(row: PriceAlertRow) -> PriceAlert:
    return PriceAlert(
        id=row.id,
        symbol=row.symbol,
        direction=AlertDirection(row.direction),
        target_price=row.target_price,
        triggered_at=row.triggered_at,
        created_at=row.created_at,
    )


def _is_triggered(price: float, direction: AlertDirection, target_price: float) -> bool:
    if direction == AlertDirection.ABOVE:
        return price >= target_price
    return price <= target_price


async def create_alert(
    session: AsyncSession,
    user_id: str,
    payload: CreateAlertRequest,
) -> PriceAlert:
    """Persist a new price alert for the authenticated user."""
    symbol = payload.symbol.upper()
    now = datetime.now(tz=UTC)
    row = PriceAlertRow(
        id=str(uuid.uuid4()),
        user_id=user_id,
        symbol=symbol,
        direction=payload.direction.value,
        target_price=payload.target_price,
        triggered_at=None,
        created_at=now,
    )
    session.add(row)
    await session.flush()
    return _row_to_model(row)


async def list_alerts(
    session: AsyncSession,
    user_id: str,
    *,
    symbol: str | None = None,
) -> list[PriceAlert]:
    """Return alerts for the user ordered by created_at descending."""
    stmt = (
        select(PriceAlertRow)
        .where(PriceAlertRow.user_id == user_id)
        .order_by(PriceAlertRow.created_at.desc())
    )
    if symbol is not None:
        stmt = stmt.where(PriceAlertRow.symbol == symbol.upper())
    result = await session.execute(stmt)
    return [_row_to_model(row) for row in result.scalars().all()]


async def delete_alert(session: AsyncSession, user_id: str, alert_id: str) -> bool:
    """Delete alert by id for the user; return False when missing."""
    row = await session.get(PriceAlertRow, alert_id)
    if row is None or row.user_id != user_id:
        return False
    await session.delete(row)
    await session.flush()
    return True


async def evaluate_pending_alerts(
    session: AsyncSession,
    user_id: str,
    provider: MarketDataProvider,
    *,
    symbol: str | None = None,
) -> None:
    """Evaluate pending alerts for the user using live quotes."""
    stmt = select(PriceAlertRow).where(
        PriceAlertRow.user_id == user_id,
        PriceAlertRow.triggered_at.is_(None),
    )
    if symbol is not None:
        stmt = stmt.where(PriceAlertRow.symbol == symbol.upper())
    result = await session.execute(stmt)
    pending_rows = list(result.scalars().all())
    if not pending_rows:
        return

    quotes_by_symbol: dict[str, float] = {}
    for row in pending_rows:
        if row.symbol in quotes_by_symbol:
            continue
        try:
            quote = await provider.get_quote(row.symbol)
        except (KeyError, Exception):
            continue
        quotes_by_symbol[row.symbol] = quote.price

    now = datetime.now(tz=UTC)
    for row in pending_rows:
        price = quotes_by_symbol.get(row.symbol)
        if price is None:
            continue
        direction = AlertDirection(row.direction)
        if _is_triggered(price, direction, row.target_price):
            row.triggered_at = now

    await session.flush()
