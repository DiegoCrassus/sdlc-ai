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
    assert payload["rebalance_summary"] == {
        "total_invested": 0.0,
        "suggestions_ready": False,
        "max_drift_percent": None,
    }
    assert payload["items"][0]["target_percent"] is None
    assert payload["items"][0]["invested_amount"] is None
    assert payload["items"][0]["current_weight_percent"] is None


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


async def _set_balanced_targets(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 50})
    await client.patch("/api/v1/watchlist/items/BTC/allocation", json={"target_percent": 50})


async def test_rebalance_zero_total_invested_has_null_weights(client: AsyncClient) -> None:
    await _set_balanced_targets(client)

    response = await client.get("/api/v1/watchlist")

    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("WatchlistResponse"))
    assert payload["rebalance_summary"] == {
        "total_invested": 0.0,
        "suggestions_ready": False,
        "max_drift_percent": None,
    }
    aapl = next(item for item in payload["items"] if item["symbol"] == "AAPL")
    assert aapl["current_weight_percent"] is None
    assert aapl["drift_percent"] is None
    assert aapl["suggestion_amount"] is None
    assert aapl["drift_band"] is None


async def test_update_invested_persists_and_enriches_response(client: AsyncClient) -> None:
    response = await client.patch(
        "/api/v1/watchlist/items/AAPL/invested",
        json={"invested_amount": 1234.56},
    )

    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("UpdateWatchlistInvestedResponse"))
    assert payload["item"]["symbol"] == "AAPL"
    assert payload["item"]["invested_amount"] == 1234.56
    assert payload["rebalance_summary"]["total_invested"] == 1234.56
    assert payload["rebalance_summary"]["suggestions_ready"] is False

    listing = await client.get("/api/v1/watchlist")
    aapl = next(item for item in listing.json()["items"] if item["symbol"] == "AAPL")
    assert aapl["invested_amount"] == 1234.56


async def test_invested_survives_target_clear(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 500})
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 25})
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": None})

    listing = await client.get("/api/v1/watchlist")
    aapl = next(item for item in listing.json()["items"] if item["symbol"] == "AAPL")
    assert aapl["target_percent"] is None
    assert aapl["invested_amount"] == 500.0


async def test_null_invested_amount_clears_value(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 100})
    response = await client.patch(
        "/api/v1/watchlist/items/AAPL/invested",
        json={"invested_amount": None},
    )

    assert response.status_code == 200
    assert response.json()["item"]["invested_amount"] is None
    assert response.json()["rebalance_summary"]["total_invested"] == 0.0


async def test_update_invested_rejects_invalid_amount(client: AsyncClient) -> None:
    for invested_amount in (-1, 10.123):
        response = await client.patch(
            "/api/v1/watchlist/items/AAPL/invested",
            json={"invested_amount": invested_amount},
        )
        assert response.status_code == 422


async def test_balanced_suggestions_when_targets_and_invested_set(client: AsyncClient) -> None:
    await _set_balanced_targets(client)
    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 600})
    await client.patch("/api/v1/watchlist/items/BTC/invested", json={"invested_amount": 400})

    response = await client.get("/api/v1/watchlist")
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("WatchlistResponse"))
    assert payload["rebalance_summary"] == {
        "total_invested": 1000.0,
        "suggestions_ready": True,
        "max_drift_percent": 10.0,
    }
    by_symbol = {item["symbol"]: item for item in payload["items"]}
    assert by_symbol["AAPL"]["current_weight_percent"] == 60.0
    assert by_symbol["BTC"]["current_weight_percent"] == 40.0
    assert by_symbol["AAPL"]["drift_percent"] == 10.0
    assert by_symbol["BTC"]["drift_percent"] == -10.0
    assert by_symbol["AAPL"]["suggestion_amount"] == -100.0
    assert by_symbol["BTC"]["suggestion_amount"] == 100.0

    suggestion_sum = sum(
        item["suggestion_amount"]
        for item in payload["items"]
        if item["suggestion_amount"] is not None
    )
    item_count = sum(1 for item in payload["items"] if item["suggestion_amount"] is not None)
    assert abs(suggestion_sum) <= 0.01 * item_count


async def test_rebalance_rounding_half_up(client: AsyncClient) -> None:
    await _set_balanced_targets(client)
    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 333.33})
    await client.patch("/api/v1/watchlist/items/BTC/invested", json={"invested_amount": 666.67})

    response = await client.get("/api/v1/watchlist")
    payload = response.json()
    assert payload["rebalance_summary"]["total_invested"] == 1000.0
    by_symbol = {item["symbol"]: item for item in payload["items"]}
    assert by_symbol["AAPL"]["current_weight_percent"] == 33.33
    assert by_symbol["BTC"]["current_weight_percent"] == 66.67
    assert by_symbol["AAPL"]["suggestion_amount"] == 166.67
    assert by_symbol["BTC"]["suggestion_amount"] == -166.67


async def test_drift_bands_on_target_warning_off_target(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 50})
    await client.patch("/api/v1/watchlist/items/MSFT/allocation", json={"target_percent": 25})
    await client.patch("/api/v1/watchlist/items/BTC/allocation", json={"target_percent": 25})

    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 4980})
    await client.patch("/api/v1/watchlist/items/MSFT/invested", json={"invested_amount": 2300})
    await client.patch("/api/v1/watchlist/items/BTC/invested", json={"invested_amount": 2720})

    response = await client.get("/api/v1/watchlist")
    by_symbol = {item["symbol"]: item for item in response.json()["items"]}

    assert by_symbol["AAPL"]["drift_band"] == "on_target"
    assert by_symbol["MSFT"]["drift_band"] == "warning"
    assert by_symbol["BTC"]["drift_band"] == "off_target"


async def test_suggestions_null_when_allocation_not_balanced(client: AsyncClient) -> None:
    await client.patch("/api/v1/watchlist/items/AAPL/allocation", json={"target_percent": 50})
    await client.patch("/api/v1/watchlist/items/AAPL/invested", json={"invested_amount": 1000})

    response = await client.get("/api/v1/watchlist")
    aapl = next(item for item in response.json()["items"] if item["symbol"] == "AAPL")
    assert response.json()["rebalance_summary"]["suggestions_ready"] is False
    assert aapl["suggestion_amount"] is None
