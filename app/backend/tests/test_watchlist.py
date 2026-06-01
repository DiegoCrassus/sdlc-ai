"""Watchlist allocation endpoint tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from httpx import AsyncClient

ALLOCATION_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "allocation.schema.json"
)


def _load_allocation_schema() -> dict[str, Any]:
    return json.loads(ALLOCATION_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_allocation_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


async def test_watchlist_includes_empty_allocation_summary(client: AsyncClient) -> None:
    response = await client.get("/api/v1/watchlist")

    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("WatchlistResponse"))
    assert payload["allocation_summary"] == {
        "target_percent_total": 0.0,
        "status": "under_allocated",
    }
    assert payload["items"][0]["target_percent"] is None


async def test_update_allocation_persists_target_and_balanced_summary(
    client: AsyncClient,
) -> None:
    first = await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": 50},
    )
    assert first.status_code == 200
    assert first.json()["allocation_summary"] == {
        "target_percent_total": 50.0,
        "status": "under_allocated",
    }

    second = await client.patch(
        "/api/v1/watchlist/items/btc/allocation",
        json={"target_percent": 50},
    )

    assert second.status_code == 200
    payload = second.json()
    jsonschema.validate(instance=payload, schema=_def_schema("UpdateWatchlistAllocationResponse"))
    assert payload["item"]["symbol"] == "BTC"
    assert payload["item"]["target_percent"] == 50.0
    assert payload["allocation_summary"] == {
        "target_percent_total": 100.0,
        "status": "balanced",
    }

    listing = await client.get("/api/v1/watchlist")
    assert listing.status_code == 200
    items_by_symbol = {item["symbol"]: item for item in listing.json()["items"]}
    assert items_by_symbol["AAPL"]["target_percent"] == 50.0
    assert items_by_symbol["BTC"]["target_percent"] == 50.0
    assert listing.json()["allocation_summary"]["status"] == "balanced"


async def test_allocation_summary_allows_over_allocation(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 75})
    response = await client.patch(
        "/api/v1/watchlist/items/MSFT/allocation",
        json={"target_percent": 25.01},
    )

    assert response.status_code == 200
    assert response.json()["allocation_summary"] == {
        "target_percent_total": 100.01,
        "status": "over_allocated",
    }


async def test_null_target_percent_clears_target(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 25})

    response = await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": None},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["item"]["symbol"] == "AAPL"
    assert payload["item"]["target_percent"] is None
    assert payload["allocation_summary"] == {
        "target_percent_total": 0.0,
        "status": "under_allocated",
    }


async def test_update_allocation_rejects_unknown_symbol(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/watchlist/items/UNKNOWN/allocation",
        json={"target_percent": 10},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_update_allocation_rejects_invalid_target_percent(client: AsyncClient) -> None:
    for target_percent in (0, 100.01, 10.123):
        response = await client.patch(
            "/api/v1/watchlist/items/AAPL/allocation",
            json={"target_percent": target_percent},
        )
        assert response.status_code == 422


async def test_update_allocation_rejects_numeric_string_target_percent(
    client: AsyncClient,
) -> None:
    response = await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": "10"},
    )

    assert response.status_code == 422


async def test_update_allocation_rejects_extra_body_properties(
    client: AsyncClient,
) -> None:
    response = await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": 10, "unexpected": "value"},
    )

    assert response.status_code == 422


async def test_update_allocation_accepts_encoded_symbol(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/watchlist/items/EUR%2FUSD/allocation",
        json={"target_percent": 1.25},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["item"]["symbol"] == "EUR/USD"
    assert payload["item"]["target_percent"] == 1.25
