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


async def create_alert(session: AsyncSession, payload: CreateAlertRequest) -> PriceAlert:
    """Persist a new price alert."""
    symbol = payload.symbol.upper()
    now = datetime.now(tz=UTC)
    row = PriceAlertRow(
        id=str(uuid.uuid4()),
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
    *,
    symbol: str | None = None,
) -> list[PriceAlert]:
    """Return alerts ordered by created_at descending."""
    stmt = select(PriceAlertRow).order_by(PriceAlertRow.created_at.desc())
    if symbol is not None:
        stmt = stmt.where(PriceAlertRow.symbol == symbol.upper())
    result = await session.execute(stmt)
    return [_row_to_model(row) for row in result.scalars().all()]


async def delete_alert(session: AsyncSession, alert_id: str) -> bool:
    """Delete alert by id; return False when missing."""
    row = await session.get(PriceAlertRow, alert_id)
    if row is None:
        return False
    await session.delete(row)
    await session.flush()
    return True


async def evaluate_pending_alerts(
    session: AsyncSession,
    provider: MarketDataProvider,
    *,
    symbol: str | None = None,
) -> None:
    """Evaluate pending alerts using live quotes; latch triggered_at on first match."""
    stmt = select(PriceAlertRow).where(PriceAlertRow.triggered_at.is_(None))
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
