"""Unit tests for watchlist rebalance pure functions."""

from __future__ import annotations

from decimal import Decimal

from marketpulse.services import watchlist_rebalance as rebalance


def test_round2_half_up() -> None:
    assert rebalance.round2(Decimal("1.005")) == Decimal("1.01")
    assert rebalance.round2(Decimal("1.004")) == Decimal("1.00")


def test_amount_cents_conversion() -> None:
    assert rebalance.amount_to_cents(Decimal("12.34")) == 1234
    assert rebalance.cents_to_amount(1234) == 12.34


def test_compute_drift_band_thresholds() -> None:
    assert rebalance.compute_drift_band(0.25) == "on_target"
    assert rebalance.compute_drift_band(-0.25) == "on_target"
    assert rebalance.compute_drift_band(0.26) == "warning"
    assert rebalance.compute_drift_band(2.0) == "warning"
    assert rebalance.compute_drift_band(-2.01) == "off_target"
    assert rebalance.compute_drift_band(None) is None
