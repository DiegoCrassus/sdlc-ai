import pytest
from sqlalchemy import delete

from app.backend.database import SessionLocal
from app.backend.models import WatchlistItemRow


@pytest.fixture(autouse=True)
async def clear_watchlist():
    async with SessionLocal() as session:
        await session.execute(delete(WatchlistItemRow))
        await session.commit()
    yield
    async with SessionLocal() as session:
        await session.execute(delete(WatchlistItemRow))
        await session.commit()


@pytest.mark.asyncio
async def test_add_and_list_with_embedded_quote(client):
    add = await client.post(
        "/api/v1/watchlist/items",
        json={"asset_id": "crypto:BTC", "notes": "Core watch", "sort_order": 0},
    )
    assert add.status_code == 201
    assert add.json()["asset_id"] == "crypto:BTC"
    assert add.json()["notes"] == "Core watch"

    listing = await client.get("/api/v1/watchlist")
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["asset_id"] == "crypto:BTC"
    assert item["asset"]["id"] == "crypto:BTC"
    assert item["asset"]["class"] == "crypto"
    assert item["quote"]["asset_id"] == "crypto:BTC"
    assert item["quote"]["source"] == "fallback"
    assert item["quote"]["price"] > 0


@pytest.mark.asyncio
async def test_duplicate_add_returns_200(client):
    first = await client.post("/api/v1/watchlist/items", json={"asset_id": "stock:AAPL"})
    assert first.status_code == 201

    second = await client.post(
        "/api/v1/watchlist/items",
        json={"asset_id": "stock:AAPL", "notes": "ignored on duplicate"},
    )
    assert second.status_code == 200
    assert second.json()["asset_id"] == "stock:AAPL"
    assert second.json().get("notes") is None or second.json()["notes"] != "ignored on duplicate"


@pytest.mark.asyncio
async def test_patch_notes(client):
    await client.post("/api/v1/watchlist/items", json={"asset_id": "crypto:ETH"})

    patched = await client.patch(
        "/api/v1/watchlist/items/crypto:ETH",
        json={"notes": "Updated note"},
    )
    assert patched.status_code == 200
    assert patched.json()["notes"] == "Updated note"


@pytest.mark.asyncio
async def test_delete_returns_204(client):
    await client.post("/api/v1/watchlist/items", json={"asset_id": "crypto:SOL"})

    deleted = await client.delete("/api/v1/watchlist/items/crypto:SOL")
    assert deleted.status_code == 204
    assert deleted.content == b""

    listing = await client.get("/api/v1/watchlist")
    assert listing.json()["total"] == 0


@pytest.mark.asyncio
async def test_post_unknown_asset_returns_404(client):
    response = await client.post(
        "/api/v1/watchlist/items",
        json={"asset_id": "stock:ZZZZ"},
    )
    assert response.status_code == 404
    err = response.json()["error"]
    assert err["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_missing_returns_404(client):
    response = await client.delete("/api/v1/watchlist/items/stock:MSFT")
    assert response.status_code == 404
    err = response.json()["error"]
    assert err["code"] == "NOT_FOUND"
