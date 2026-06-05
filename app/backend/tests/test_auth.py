"""Auth endpoint tests (INVES-114)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema
from auth_helpers import identify_as
from httpx import AsyncClient

AUTH_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "auth.schema.json"
)


def _load_auth_schema() -> dict[str, Any]:
    return json.loads(AUTH_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_auth_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


async def test_identify_returns_200_and_set_cookie(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/identify",
        json={"email": "User@Example.com"},
    )
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("IdentifyResponse"))
    assert payload["user"]["email"] == "user@example.com"
    assert "mp_session" in response.cookies
    assert response.cookies["mp_session"]


async def test_me_without_cookie_returns_401_session_error(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("SessionError"))
    assert payload["error"]["code"] == "UNAUTHORIZED"


async def test_me_with_cookie_returns_user(client: AsyncClient) -> None:
    await identify_as(client, "me@example.com")
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("AuthMeResponse"))
    assert payload["user"]["email"] == "me@example.com"


async def test_logout_clears_session(client: AsyncClient) -> None:
    await identify_as(client, "logout@example.com")
    logout = await client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert logout.content == b""

    me = await client.get("/api/v1/auth/me")
    assert me.status_code == 401


async def test_watchlist_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/watchlist")
    assert response.status_code == 401
    payload = response.json()
    jsonschema.validate(instance=payload, schema=_def_schema("SessionError"))
    assert payload["error"]["code"] == "UNAUTHORIZED"


async def test_alerts_require_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/alerts")
    assert response.status_code == 401


async def test_two_users_have_isolated_watchlist(client: AsyncClient) -> None:
    await identify_as(client, "alice@example.com")
    await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": 75},
    )

    await identify_as(client, "bob@example.com")
    listing = await client.get("/api/v1/watchlist")
    assert listing.status_code == 200
    aapl = next(item for item in listing.json()["items"] if item["symbol"] == "AAPL")
    assert aapl["target_percent"] is None

    await client.patch(
        "/api/v1/watchlist/items/AAPL/allocation",
        json={"target_percent": 25},
    )

    await identify_as(client, "alice@example.com")
    alice_listing = await client.get("/api/v1/watchlist")
    alice_aapl = next(
        item for item in alice_listing.json()["items"] if item["symbol"] == "AAPL"
    )
    assert alice_aapl["target_percent"] == 75.0


async def test_two_users_have_isolated_alerts(client: AsyncClient) -> None:
    await identify_as(client, "alice@example.com")
    create = await client.post(
        "/api/v1/alerts",
        json={"symbol": "BTC", "direction": "above", "target_price": 60_000},
    )
    assert create.status_code == 201
    alice_alert_id = create.json()["id"]

    await identify_as(client, "bob@example.com")
    bob_listing = await client.get("/api/v1/alerts")
    assert bob_listing.status_code == 200
    assert bob_listing.json()["items"] == []

    bob_create = await client.post(
        "/api/v1/alerts",
        json={"symbol": "ETH", "direction": "below", "target_price": 3_000},
    )
    assert bob_create.status_code == 201

    await identify_as(client, "alice@example.com")
    alice_listing = await client.get("/api/v1/alerts")
    assert len(alice_listing.json()["items"]) == 1
    assert alice_listing.json()["items"][0]["id"] == alice_alert_id
    assert alice_listing.json()["items"][0]["symbol"] == "BTC"

    await identify_as(client, "bob@example.com")
    bob_listing = await client.get("/api/v1/alerts")
    assert len(bob_listing.json()["items"]) == 1
    assert bob_listing.json()["items"][0]["symbol"] == "ETH"
