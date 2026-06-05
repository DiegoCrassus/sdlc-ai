"""Portfolio snapshot persistence and history (INVES-118)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.db.models import PortfolioSnapshotRow
from marketpulse.domain.models import (
    CreateSnapshotResponse,
    HistoryDays,
    PortfolioHistoryPoint,
    PortfolioHistoryResponse,
    PortfolioHistorySummary,
    PortfolioSnapshot,
)
from marketpulse.domain.watchlist import DEFAULT_WATCHLIST
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services.watchlist_rebalance import cents_to_amount, round2

logger = logging.getLogger(__name__)

_TWO_PLACES = Decimal("0.01")


def utc_today() -> date:
    """Return the current UTC calendar date."""
    return datetime.now(tz=UTC).date()


def cents_to_wire_amount(cents: int) -> float:
    """Convert stored integer cents to a wire amount with two decimal places."""
    return cents_to_amount(cents)


def wire_amount_to_cents(amount: Decimal) -> int:
    """Convert a currency amount to integer cents with ROUND_HALF_UP."""
    return int(round2(amount) * 100)


def _pct_change(current: Decimal, baseline: Decimal) -> float:
    if baseline == 0:
        return 0.0
    value = (current / baseline - Decimal("1")) * Decimal("100")
    return float(round2(value))


async def compute_total_value_cents(
    provider: MarketDataProvider,
    invested_cents_by_symbol: dict[str, int],
) -> int:
    """Sum price × invested_amount for default watchlist symbols."""
    total = Decimal("0")
    for symbol in DEFAULT_WATCHLIST:
        invested_cents = invested_cents_by_symbol.get(symbol, 0)
        invested_amount = Decimal(invested_cents) / Decimal("100")
        quote = await provider.get_quote(symbol)
        total += Decimal(str(quote.price)) * invested_amount
    return wire_amount_to_cents(total)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _row_to_snapshot(row: PortfolioSnapshotRow) -> PortfolioSnapshot:
    return PortfolioSnapshot(
        snapshot_date=row.snapshot_date,
        total_value=cents_to_wire_amount(row.total_value_cents),
        created_at=_ensure_utc(row.created_at),
        updated_at=_ensure_utc(row.updated_at),
    )


async def _get_snapshot_row(
    session: AsyncSession,
    *,
    user_id: str,
    snapshot_date: date,
) -> PortfolioSnapshotRow | None:
    stmt = select(PortfolioSnapshotRow).where(
        PortfolioSnapshotRow.user_id == user_id,
        PortfolioSnapshotRow.snapshot_date == snapshot_date,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def record_snapshot(
    session: AsyncSession,
    user_id: str,
    provider: MarketDataProvider,
    invested_cents_by_symbol: dict[str, int],
    *,
    upsert: bool = True,
    snapshot_date: date | None = None,
) -> CreateSnapshotResponse:
    """Insert or upsert a snapshot for the given UTC calendar day."""
    target_date = snapshot_date or utc_today()
    total_value_cents = await compute_total_value_cents(provider, invested_cents_by_symbol)
    now = datetime.now(tz=UTC)
    existing = await _get_snapshot_row(session, user_id=user_id, snapshot_date=target_date)
    if existing is None:
        row = PortfolioSnapshotRow(
            id=str(uuid.uuid4()),
            user_id=user_id,
            snapshot_date=target_date,
            total_value_cents=total_value_cents,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()
        return CreateSnapshotResponse(snapshot=_row_to_snapshot(row), created=True)

    if not upsert:
        return CreateSnapshotResponse(snapshot=_row_to_snapshot(existing), created=False)

    existing.total_value_cents = total_value_cents
    existing.updated_at = now
    await session.flush()
    return CreateSnapshotResponse(snapshot=_row_to_snapshot(existing), created=False)


async def ensure_daily_snapshot(
    session: AsyncSession,
    user_id: str,
    provider: MarketDataProvider,
    invested_cents_by_symbol: dict[str, int],
) -> CreateSnapshotResponse | None:
    """Insert today's snapshot only when none exists for the user."""
    target_date = utc_today()
    existing = await _get_snapshot_row(session, user_id=user_id, snapshot_date=target_date)
    if existing is not None:
        return None
    return await record_snapshot(
        session,
        user_id,
        provider,
        invested_cents_by_symbol,
        upsert=False,
        snapshot_date=target_date,
    )


def enrich_history_points(rows: list[PortfolioSnapshotRow]) -> list[PortfolioHistoryPoint]:
    """Attach daily and cumulative return percentages to ascending snapshot rows."""
    if not rows:
        return []

    points: list[PortfolioHistoryPoint] = []
    first_value = Decimal(rows[0].total_value_cents) / Decimal("100")
    previous_value = first_value

    for index, row in enumerate(rows):
        wire_value = cents_to_wire_amount(row.total_value_cents)
        value = Decimal(row.total_value_cents) / Decimal("100")
        if index == 0:
            daily_pct = 0.0
            cumulative_pct = 0.0
        else:
            daily_pct = _pct_change(value, previous_value)
            cumulative_pct = _pct_change(value, first_value)
            previous_value = value
        points.append(
            PortfolioHistoryPoint(
                snapshot_date=row.snapshot_date,
                total_value=wire_value,
                daily_change_pct=daily_pct,
                cumulative_return_pct=cumulative_pct,
            )
        )
    return points


def _find_closest_row(
    rows: list[PortfolioSnapshotRow],
    target_date: date,
) -> PortfolioSnapshotRow | None:
    if not rows:
        return None
    return min(rows, key=lambda row: abs((row.snapshot_date - target_date).days))


def _compute_summary(
    rows: list[PortfolioSnapshotRow],
    *,
    today: date,
) -> PortfolioHistorySummary | None:
    if len(rows) < 2:
        return None

    latest = rows[-1]
    latest_value = Decimal(latest.total_value_cents) / Decimal("100")
    summary = PortfolioHistorySummary()

    previous_rows = [row for row in rows if row.snapshot_date < latest.snapshot_date]
    if previous_rows:
        previous = previous_rows[-1]
        previous_value = Decimal(previous.total_value_cents) / Decimal("100")
        summary.pnl_today = float(round2(latest_value - previous_value))

    row_7d = _find_closest_row(rows[:-1], today - timedelta(days=7))
    if row_7d is not None:
        baseline = Decimal(row_7d.total_value_cents) / Decimal("100")
        summary.pnl_7d = float(round2(latest_value - baseline))

    row_30d = _find_closest_row(rows[:-1], today - timedelta(days=30))
    if row_30d is not None:
        baseline = Decimal(row_30d.total_value_cents) / Decimal("100")
        summary.pnl_30d = float(round2(latest_value - baseline))

    ytd_start = date(today.year, 1, 1)
    ytd_rows = [row for row in rows if row.snapshot_date >= ytd_start]
    if ytd_rows and ytd_rows[0].snapshot_date < latest.snapshot_date:
        baseline = Decimal(ytd_rows[0].total_value_cents) / Decimal("100")
        summary.pnl_ytd = float(round2(latest_value - baseline))

    if all(
        value is None
        for value in (summary.pnl_today, summary.pnl_7d, summary.pnl_30d, summary.pnl_ytd)
    ):
        return None
    return summary


async def get_history(
    session: AsyncSession,
    user_id: str,
    days: HistoryDays = 30,
) -> PortfolioHistoryResponse:
    """Return ascending snapshot history within the requested UTC day window."""
    today = utc_today()
    start_date = today - timedelta(days=days - 1)
    stmt = (
        select(PortfolioSnapshotRow)
        .where(
            PortfolioSnapshotRow.user_id == user_id,
            PortfolioSnapshotRow.snapshot_date >= start_date,
            PortfolioSnapshotRow.snapshot_date <= today,
        )
        .order_by(PortfolioSnapshotRow.snapshot_date.asc())
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    points = enrich_history_points(rows)
    summary = _compute_summary(rows, today=today)
    return PortfolioHistoryResponse(days=days, points=points, summary=summary)
