"""Price alert endpoint tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from httpx import AsyncClient
from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.enums import AlertDirection, AssetClass, DataSource
from marketpulse.domain.models import Quote, SourceMeta
from marketpulse.main import app
from marketpulse.providers.base import MarketDataProvider

ALERTS_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "alerts.schema.json"
)


def _load_alerts_schema() -> dict[str, Any]:
    return json.loads(ALERTS_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_alerts_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


class FixedQuoteProvider(MarketDataProvider):
    """Provider with configurable per-symbol prices for trigger tests."""

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
            asset_class=AssetClass.CRYPTO,
            price=price,
            change=0.0,
            change_percent=0.0,
            meta=SourceMeta(
                source=DataSource.MOCK,
                provider=self.provider_name,
                fetched_at=datetime.now(tz=UTC),
            ),
        )

    async def get_overview(self):  # pragma: no cover - not used in alert tests
        raise NotImplementedError

    async def get_ohlcv(self, symbol: str, interval, limit: int):  # pragma: no cover
        raise NotImplementedError

    async def search(self, query: str):  # pragma: no cover
        raise NotImplementedError

    async def get_projection(self, symbol: str, horizon_days: int):  # pragma: no cover
        raise NotImplementedError


@pytest.fixture
def fixed_provider() -> FixedQuoteProvider:
    return FixedQuoteProvider({"BTC": 50_000.0, "AAPL": 200.0})


@pytest.fixture
def client_with_fixed_provider(fixed_provider: FixedQuoteProvider, client: AsyncClient):
    app.dependency_overrides[get_market_provider_dep] = lambda: fixed_provider
    yield client
    app.dependency_overrides.clear()


async def test_create_alert_returns_201(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 60_000},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["symbol"] == "BTC"
    assert payload["direction"] == "above"
    assert payload["target_price"] == 60_000
    assert payload["triggered_at"] is None
    assert "id" in payload
    assert "created_at" in payload
    jsonschema.validate(instance=payload, schema=_def_schema("PriceAlert"))


async def test_create_alert_rejects_non_watchlist_symbol(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alerts",
        json={"symbol": "UNKNOWN", "direction": "above", "target_price": 100},
    )
    assert response.status_code == 400
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("AlertError"))
    assert payload["error"]["code"] == "VALIDATION_ERROR"


async def test_create_alert_rejects_invalid_target_price(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 0},
    )
    assert response.status_code == 422


async def test_list_alerts_empty(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    payload = response.json()
    assert payload == {"items": []}
    jsonschema.validate(instance=payload, schema=_def_schema("AlertListResponse"))


async def test_list_alerts_evaluates_above_trigger(
    client_with_fixed_provider: AsyncClient,
) -> None:
    create = await client_with_fixed_provider.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 49_000},
    )
    assert create.status_code == 201

    response = await client_with_fixed_provider.get("/api/v1/alerts")
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("AlertListResponse"))
    assert len(payload["items"]) == 1
    assert payload["items"][0]["triggered_at"] is not None


async def test_list_alerts_evaluates_below_trigger(
    client_with_fixed_provider: AsyncClient,
) -> None:
    create = await client_with_fixed_provider.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "below", "target_price": 51_000},
    )
    assert create.status_code == 201

    response = await client_with_fixed_provider.get("/api/v1/alerts")
    assert response.status_code == 200
    assert response.json()["items"][0]["triggered_at"] is not None


async def test_triggered_alert_is_not_re_evaluated(
    client_with_fixed_provider: AsyncClient,
) -> None:
    create = await client_with_fixed_provider.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 49_000},
    )
    assert create.status_code == 201

    first = await client_with_fixed_provider.get("/api/v1/alerts")
    triggered_at = first.json()["items"][0]["triggered_at"]
    assert triggered_at is not None

    app.dependency_overrides[get_market_provider_dep] = lambda: FixedQuoteProvider({"BTC": 1.0})
    second = await client_with_fixed_provider.get("/api/v1/alerts")
    assert second.json()["items"][0]["triggered_at"] == triggered_at


async def test_list_alerts_filters_by_symbol(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 70_000},
    )
    await client.post(
        "/api/v1/alerts",
        json={"symbol": "AAPL", "direction": "below", "target_price": 150},
    )

    response = await client.get("/api/v1/alerts", params={"symbol": "BTC"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["symbol"] == "BTC"


async def test_delete_alert_returns_204(client: AsyncClient) -> None:
    create = await client.post(
        "/api/v1/alerts",
        json={"symbol": "ETH", "direction": "above", "target_price": 5_000},
    )
    alert_id = create.json()["id"]

    delete = await client.delete(f"/api/v1/alerts/{alert_id}")
    assert delete.status_code == 204
    assert delete.content == b""

    listing = await client.get("/api/v1/alerts")
    assert listing.json()["items"] == []


async def test_delete_alert_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/alerts/00000000-0000-4000-8000-000000000000")
    assert response.status_code == 404
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("AlertError"))
    assert payload["error"]["code"] == "NOT_FOUND"


async def test_service_trigger_logic() -> None:
    from marketpulse.services.alerts import _is_triggered

    assert _is_triggered(100.0, AlertDirection.ABOVE, 100.0) is True
    assert _is_triggered(99.9, AlertDirection.ABOVE, 100.0) is False
    assert _is_triggered(100.0, AlertDirection.BELOW, 100.0) is True
    assert _is_triggered(100.1, AlertDirection.BELOW, 100.0) is False
