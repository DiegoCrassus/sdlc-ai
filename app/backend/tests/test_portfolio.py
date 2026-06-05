"""Portfolio snapshot endpoint tests."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from httpx import AsyncClient
from marketpulse.db.models import PortfolioSnapshotRow
from marketpulse.db.session import get_session_factory
from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.enums import AssetClass, DataSource
from marketpulse.domain.models import Quote, SourceMeta
from marketpulse.domain.watchlist import DEFAULT_WATCHLIST
from marketpulse.main import app
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services import portfolio_snapshots as snapshot_service

PORTFOLIO_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "portfolio.schema.json"
)


def _load_portfolio_schema() -> dict[str, Any]:
    return json.loads(PORTFOLIO_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_portfolio_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


class FixedQuoteProvider(MarketDataProvider):
    """Provider with deterministic per-symbol prices."""

    def __init__(self, prices: dict[str, float]) -> None:
        self._prices = {symbol.upper(): price for symbol, price in prices.items()}

    @property
    def provider_name(self) -> str:
        return "fixed"

    async def get_quote(self, symbol: str) -> Quote:
        key = symbol.upper()
        if key not in self._prices:
            raise KeyError(f"Unknown symbol: {symbol}")
        price = self._prices[key]
        return Quote(
            asset_id=key,
            symbol=key,
            name=key,
            asset_class=AssetClass.STOCK,
            price=price,
            change=0.0,
            change_percent=0.0,
            meta=SourceMeta(
                source=DataSource.MOCK,
                provider=self.provider_name,
                fetched_at=datetime.now(tz=UTC),
            ),
        )

    async def get_overview(self):  # pragma: no cover
        raise NotImplementedError

    async def get_ohlcv(self, symbol: str, interval, limit: int):  # pragma: no cover
        raise NotImplementedError

    async def search(self, query: str):  # pragma: no cover
        raise NotImplementedError

    async def get_projection(self, symbol: str, horizon_days: int):  # pragma: no cover
        raise NotImplementedError


FIXED_PRICES: dict[str, float] = {
    "AAPL": 100.0,
    "MSFT": 200.0,
    "NVDA": 300.0,
    "BTC": 50_000.0,
    "ETH": 3_000.0,
    "SOL": 150.0,
    "EUR/USD": 1.0,
}


@pytest.fixture
def fixed_provider() -> FixedQuoteProvider:
    return FixedQuoteProvider(FIXED_PRICES)


@pytest.fixture
def override_provider(fixed_provider: FixedQuoteProvider):
    app.dependency_overrides[get_market_provider_dep] = lambda: fixed_provider
    yield fixed_provider
    app.dependency_overrides.pop(get_market_provider_dep, None)


def _expected_total_cents(
    prices: dict[str, float],
    invested_cents_by_symbol: dict[str, int],
) -> int:
    total = 0.0
    for symbol in DEFAULT_WATCHLIST:
        invested = invested_cents_by_symbol.get(symbol, 0) / 100
        total += prices[symbol] * invested
    return int(round(total * 100))


async def _current_user_id(client: AsyncClient) -> str:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    return response.json()["user"]["id"]


async def _seed_snapshots(
    user_id: str,
    *,
    today: date,
    values_cents: list[int],
) -> None:
    factory = get_session_factory()
    async with factory() as session:
        now = datetime.combine(today, datetime.min.time(), tzinfo=UTC)
        for offset, cents in enumerate(values_cents):
            snapshot_date = today - timedelta(days=len(values_cents) - 1 - offset)
            session.add(
                PortfolioSnapshotRow(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    snapshot_date=snapshot_date,
                    total_value_cents=cents,
                    created_at=now,
                    updated_at=now,
                )
            )
        await session.commit()


async def test_compute_total_value_cents_matches_price_times_invested(
    fixed_provider: FixedQuoteProvider,
) -> None:
    invested = {"AAPL": 10_000, "BTC": 50}
    expected = _expected_total_cents(FIXED_PRICES, invested)
    actual = await snapshot_service.compute_total_value_cents(fixed_provider, invested)
    assert actual == expected


async def test_post_snapshot_creates_and_upserts(
    authed_client: AsyncClient,
    override_provider: FixedQuoteProvider,
) -> None:
    await authed_client.patch(
        "/api/v1/watchlist/items/AAPL/invested",
        json={"invested_amount": 100.0},
    )
    await authed_client.patch(
        "/api/v1/watchlist/items/BTC/invested",
        json={"invested_amount": 0.5},
    )

    first = await authed_client.post("/api/v1/portfolio/snapshots")
    assert first.status_code == 200
    first_payload = first.json()
    jsonschema.validate(instance=first_payload, schema=_def_schema("CreateSnapshotResponse"))
    assert first_payload["created"] is True
    assert first_payload["snapshot"]["total_value"] == 35_000.0

    second = await authed_client.post("/api/v1/portfolio/snapshots")
    assert second.status_code == 200
    second_payload = second.json()
    jsonschema.validate(instance=second_payload, schema=_def_schema("CreateSnapshotResponse"))
    assert second_payload["created"] is False
    assert second_payload["snapshot"]["snapshot_date"] == first_payload["snapshot"]["snapshot_date"]
    assert second_payload["snapshot"]["created_at"] == first_payload["snapshot"]["created_at"]


async def test_get_history_returns_pct_fields(
    authed_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    today = date(2026, 6, 5)
    monkeypatch.setattr(snapshot_service, "utc_today", lambda: today)
    user_id = await _current_user_id(authed_client)
    await _seed_snapshots(user_id, today=today, values_cents=[10_000, 12_000, 11_000, 15_000])

    response = await authed_client.get("/api/v1/portfolio/history?days=30")
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("PortfolioHistoryResponse"))
    assert payload["days"] == 30
    assert len(payload["points"]) == 4
    assert payload["points"][0]["daily_change_pct"] == 0.0
    assert payload["points"][0]["cumulative_return_pct"] == 0.0
    assert payload["points"][1]["daily_change_pct"] == 20.0
    assert payload["points"][1]["cumulative_return_pct"] == 20.0
    assert payload["points"][2]["daily_change_pct"] == pytest.approx(-8.33)
    assert payload["points"][2]["cumulative_return_pct"] == 10.0
    assert payload["points"][3]["daily_change_pct"] == pytest.approx(36.36)
    assert payload["points"][3]["cumulative_return_pct"] == 50.0


async def test_seven_snapshots_return_seven_points(
    authed_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    today = date(2026, 6, 7)
    monkeypatch.setattr(snapshot_service, "utc_today", lambda: today)
    user_id = await _current_user_id(authed_client)
    await _seed_snapshots(
        user_id,
        today=today,
        values_cents=[10_000 + index * 100 for index in range(7)],
    )

    response = await authed_client.get("/api/v1/portfolio/history?days=30")
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("PortfolioHistoryResponse"))
    assert len(payload["points"]) == 7


async def test_portfolio_routes_require_auth(client: AsyncClient) -> None:
    assert (await client.post("/api/v1/portfolio/snapshots")).status_code == 401
    assert (await client.get("/api/v1/portfolio/history")).status_code == 401
