"""Watchlist allocation target persistence and summary helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.db.models import WatchlistAllocationTargetRow
from marketpulse.domain.models import WatchlistAllocationSummary

BALANCED_TARGET_BPS = 10_000


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


async def list_targets(session: AsyncSession) -> dict[str, int]:
    """Return saved allocation targets keyed by normalized symbol."""
    result = await session.execute(select(WatchlistAllocationTargetRow))
    return {row.symbol: row.target_bps for row in result.scalars().all()}


async def set_target(
    session: AsyncSession,
    *,
    symbol: str,
    target_bps: int | None,
) -> dict[str, int]:
    """Set or clear a target, returning the current target map."""
    normalized = symbol.upper()
    row = await session.get(WatchlistAllocationTargetRow, normalized)
    if target_bps is None:
        if row is not None:
            await session.delete(row)
    elif row is None:
        session.add(
            WatchlistAllocationTargetRow(
                symbol=normalized,
                target_bps=target_bps,
                updated_at=datetime.now(tz=UTC),
            )
        )
    else:
        row.target_bps = target_bps
        row.updated_at = datetime.now(tz=UTC)
    await session.flush()
    return await list_targets(session)
