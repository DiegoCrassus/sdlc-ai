"""Watchlist allocation target persistence and summary helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.db.models import WatchlistAllocationTargetRow, WatchlistInvestedAmountRow
from marketpulse.domain.models import WatchlistAllocationSummary

BALANCED_TARGET_BPS = 10_000
_TWO_PLACES = Decimal("0.01")


def target_percent_to_bps(target_percent: Decimal) -> int:
    """Convert validated public decimal percent to integer basis points."""
    return int(target_percent * Decimal("100"))


def bps_to_target_percent(target_bps: int) -> float:
    return target_bps / 100


def build_allocation_summary(targets_by_symbol: dict[str, int]) -> WatchlistAllocationSummary:
    total_bps = sum(targets_by_symbol.values())
    if total_bps == BALANCED_TARGET_BPS:
        status = "balanced"
    elif total_bps < BALANCED_TARGET_BPS:
        status = "under_allocated"
    else:
        status = "over_allocated"
    return WatchlistAllocationSummary(
        target_percent_total=bps_to_target_percent(total_bps),
        status=status,
    )


async def list_targets(session: AsyncSession, user_id: str) -> dict[str, int]:
    """Return saved allocation targets for the user keyed by normalized symbol."""
    stmt = select(WatchlistAllocationTargetRow).where(
        WatchlistAllocationTargetRow.user_id == user_id
    )
    result = await session.execute(stmt)
    return {row.symbol: row.target_bps for row in result.scalars().all()}


async def set_target(
    session: AsyncSession,
    *,
    user_id: str,
    symbol: str,
    target_bps: int | None,
) -> dict[str, int]:
    """Set or clear a target for the user, returning the current target map."""
    normalized = symbol.upper()
    row = await session.get(WatchlistAllocationTargetRow, (user_id, normalized))
    if target_bps is None:
        if row is not None:
            await session.delete(row)
    elif row is None:
        session.add(
            WatchlistAllocationTargetRow(
                user_id=user_id,
                symbol=normalized,
                target_bps=target_bps,
                updated_at=datetime.now(tz=UTC),
            )
        )
    else:
        row.target_bps = target_bps
        row.updated_at = datetime.now(tz=UTC)
    await session.flush()
    return await list_targets(session, user_id)


async def list_invested(session: AsyncSession, user_id: str) -> dict[str, int]:
    """Return saved invested amounts for the user keyed by symbol (cents)."""
    stmt = select(WatchlistInvestedAmountRow).where(
        WatchlistInvestedAmountRow.user_id == user_id
    )
    result = await session.execute(stmt)
    return {row.symbol: row.amount_cents for row in result.scalars().all()}


async def set_invested(
    session: AsyncSession,
    *,
    user_id: str,
    symbol: str,
    amount_cents: int | None,
) -> dict[str, int]:
    """Set or clear an invested amount for the user, returning the current map."""
    normalized = symbol.upper()
    row = await session.get(WatchlistInvestedAmountRow, (user_id, normalized))
    if amount_cents is None:
        if row is not None:
            await session.delete(row)
    elif row is None:
        session.add(
            WatchlistInvestedAmountRow(
                user_id=user_id,
                symbol=normalized,
                amount_cents=amount_cents,
                updated_at=datetime.now(tz=UTC),
            )
        )
    else:
        row.amount_cents = amount_cents
        row.updated_at = datetime.now(tz=UTC)
    await session.flush()
    return await list_invested(session, user_id)


def invested_amount_to_cents(invested_amount: Decimal) -> int:
    """Convert validated public decimal amount to integer cents."""
    rounded = invested_amount.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    return int(rounded * 100)
