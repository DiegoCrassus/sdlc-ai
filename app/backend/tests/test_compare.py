"""Compare endpoint and service unit tests."""

from __future__ import annotations

import math

from httpx import AsyncClient
from marketpulse.services.compare import (
    compute_max_drawdown,
    compute_volatility,
    normalize_points,
    pearson_correlation,
)


def test_normalize_points_first_close_is_100() -> None:
    assert normalize_points([50.0, 75.0, 100.0]) == [100.0, 150.0, 200.0]
    assert normalize_points([200.0, 180.0, 220.0])[0] == 100.0


def test_normalize_points_single_value() -> None:
    assert normalize_points([42.0]) == [100.0]


def test_pearson_perfect_positive_correlation() -> None:
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    assert math.isclose(pearson_correlation(x, y), 1.0, rel_tol=1e-9)


def test_pearson_perfect_negative_correlation() -> None:
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y = [5.0, 4.0, 3.0, 2.0, 1.0]
    assert math.isclose(pearson_correlation(x, y), -1.0, rel_tol=1e-9)


def test_pearson_zero_variance_returns_zero() -> None:
    assert pearson_correlation([1.0, 1.0, 1.0], [2.0, 3.0, 4.0]) == 0.0


def test_compute_volatility_positive_for_varying_closes() -> None:
    closes = [100.0, 101.0, 99.5, 102.0, 100.5]
    assert compute_volatility(closes) > 0


def test_compute_max_drawdown_peak_to_trough() -> None:
    closes = [100.0, 120.0, 90.0, 110.0]
    assert math.isclose(compute_max_drawdown(closes), 25.0, rel_tol=1e-9)


async def test_compare_btc_eth_returns_200(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/markets/compare",
        params={"symbols": "BTC,ETH", "days": 30},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["symbols"] == ["BTC", "ETH"]
    assert payload["days"] == 30
    assert len(payload["series"]) == 2
    assert {series["symbol"] for series in payload["series"]} == {"BTC", "ETH"}

    for series in payload["series"]:
        assert len(series["points"]) >= 2
        assert series["points"][0]["normalized_close"] == 100.0
        first_point = series["points"][0]
        assert {"date", "normalized_close", "open", "high", "low", "volume"} <= set(
            first_point.keys()
        )

    correlation = payload["correlation"]
    assert correlation["symbols"] == ["BTC", "ETH"]
    assert len(correlation["values"]) == 2
    assert len(correlation["values"][0]) == 2
    assert correlation["values"][0][0] == 1.0
    assert correlation["values"][1][1] == 1.0
    assert -1.0 <= correlation["values"][0][1] <= 1.0

    assert len(payload["metrics"]) == 2
    assert payload["date_range"]["aligned_points"] >= 2
    assert payload["meta"]["provider"] == "mock"


async def test_compare_one_symbol_returns_422(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/markets/compare",
        params={"symbols": "BTC"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "invalid_symbol_count"


async def test_compare_five_symbols_returns_422(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/markets/compare",
        params={"symbols": "BTC,ETH,SOL,AAPL,MSFT"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "invalid_symbol_count"


async def test_compare_unknown_symbol_returns_404(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/markets/compare",
        params={"symbols": "BTC,UNKNOWN"},
    )
    assert response.status_code == 404
