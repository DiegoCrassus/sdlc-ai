"""Pure rebalance computation for watchlist invested amounts (ADR-012)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from marketpulse.domain.models import RebalanceSummary, WatchlistAllocationSummary
from marketpulse.services.watchlist_allocations import bps_to_target_percent

DriftBand = Literal["on_target", "warning", "off_target"]

_ON_TARGET_THRESHOLD = Decimal("0.25")
_WARNING_THRESHOLD = Decimal("2.0")
_TWO_PLACES = Decimal("0.01")


def round2(value: Decimal) -> Decimal:
    """Round to two decimal places with ROUND_HALF_UP."""
    return value.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


def cents_to_amount(cents: int) -> float:
    """Convert stored integer cents to a wire amount with two decimal places."""
    return float(round2(Decimal(cents) / Decimal("100")))


def amount_to_cents(amount: Decimal) -> int:
    """Convert a validated wire amount to integer cents."""
    return int(round2(amount) * 100)


def invested_amount_for_symbol(invested_cents_by_symbol: dict[str, int], symbol: str) -> Decimal:
    """Return invested amount in currency units; missing symbols count as zero."""
    return Decimal(invested_cents_by_symbol.get(symbol, 0)) / Decimal("100")


def compute_total_invested(invested_cents_by_symbol: dict[str, int]) -> Decimal:
    """Sum all invested amounts; empty map yields zero."""
    total_cents = sum(invested_cents_by_symbol.values())
    return Decimal(total_cents) / Decimal("100")


def compute_current_weight_percent(
    invested_amount: Decimal,
    total_invested: Decimal,
) -> float | None:
    if total_invested == 0:
        return None
    return float(round2(invested_amount / total_invested * Decimal("100")))


def compute_drift_percent(
    current_weight_percent: float | None,
    target_percent: float | None,
    total_invested: Decimal,
) -> float | None:
    if target_percent is None or total_invested == 0 or current_weight_percent is None:
        return None
    return float(round2(Decimal(str(current_weight_percent)) - Decimal(str(target_percent))))


def compute_suggestion_amount(
    *,
    target_percent: float | None,
    total_invested: Decimal,
    invested_amount: Decimal,
    suggestions_ready: bool,
) -> float | None:
    if not suggestions_ready or target_percent is None or total_invested == 0:
        return None
    target_value = Decimal(str(target_percent)) / Decimal("100") * total_invested
    return float(round2(target_value - invested_amount))


def compute_drift_band(drift_percent: float | None) -> DriftBand | None:
    if drift_percent is None:
        return None
    magnitude = abs(Decimal(str(drift_percent)))
    if magnitude <= _ON_TARGET_THRESHOLD:
        return "on_target"
    if magnitude <= _WARNING_THRESHOLD:
        return "warning"
    return "off_target"


@dataclass(frozen=True)
class ItemRebalanceFields:
    invested_amount: float | None
    current_weight_percent: float | None
    drift_percent: float | None
    suggestion_amount: float | None
    drift_band: DriftBand | None


def compute_item_rebalance(
    *,
    symbol: str,
    target_bps: int | None,
    invested_cents_by_symbol: dict[str, int],
    total_invested: Decimal,
    suggestions_ready: bool,
) -> ItemRebalanceFields:
    invested_cents = invested_cents_by_symbol.get(symbol)
    invested_amount_wire = cents_to_amount(invested_cents) if invested_cents is not None else None
    invested_amount = invested_amount_for_symbol(invested_cents_by_symbol, symbol)
    target_percent = bps_to_target_percent(target_bps) if target_bps is not None else None
    current_weight = compute_current_weight_percent(invested_amount, total_invested)
    drift = compute_drift_percent(current_weight, target_percent, total_invested)
    suggestion = compute_suggestion_amount(
        target_percent=target_percent,
        total_invested=total_invested,
        invested_amount=invested_amount,
        suggestions_ready=suggestions_ready,
    )
    return ItemRebalanceFields(
        invested_amount=invested_amount_wire,
        current_weight_percent=current_weight,
        drift_percent=drift,
        suggestion_amount=suggestion,
        drift_band=compute_drift_band(drift),
    )


def compute_rebalance_summary(
    *,
    symbols: list[str],
    targets_by_symbol: dict[str, int],
    invested_cents_by_symbol: dict[str, int],
    allocation_summary: WatchlistAllocationSummary,
) -> RebalanceSummary:
    total_invested = compute_total_invested(invested_cents_by_symbol)
    suggestions_ready = total_invested > 0 and allocation_summary.status == "balanced"
    drift_values: list[float] = []
    for symbol in symbols:
        target_bps = targets_by_symbol.get(symbol)
        invested_amount = invested_amount_for_symbol(invested_cents_by_symbol, symbol)
        target_percent = bps_to_target_percent(target_bps) if target_bps is not None else None
        current_weight = compute_current_weight_percent(invested_amount, total_invested)
        drift = compute_drift_percent(current_weight, target_percent, total_invested)
        if drift is not None:
            drift_values.append(abs(drift))
    max_drift = max(drift_values) if drift_values else None
    return RebalanceSummary(
        total_invested=float(round2(total_invested)),
        suggestions_ready=suggestions_ready,
        max_drift_percent=max_drift,
    )


def compute_all_item_rebalances(
    *,
    symbols: list[str],
    targets_by_symbol: dict[str, int],
    invested_cents_by_symbol: dict[str, int],
    allocation_summary: WatchlistAllocationSummary,
) -> tuple[dict[str, ItemRebalanceFields], RebalanceSummary]:
    total_invested = compute_total_invested(invested_cents_by_symbol)
    suggestions_ready = total_invested > 0 and allocation_summary.status == "balanced"
    items: dict[str, ItemRebalanceFields] = {}
    for symbol in symbols:
        items[symbol] = compute_item_rebalance(
            symbol=symbol,
            target_bps=targets_by_symbol.get(symbol),
            invested_cents_by_symbol=invested_cents_by_symbol,
            total_invested=total_invested,
            suggestions_ready=suggestions_ready,
        )
    summary = compute_rebalance_summary(
        symbols=symbols,
        targets_by_symbol=targets_by_symbol,
        invested_cents_by_symbol=invested_cents_by_symbol,
        allocation_summary=allocation_summary,
    )
    return items, summary
