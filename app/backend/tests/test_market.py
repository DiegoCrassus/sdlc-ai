import pytest


@pytest.mark.asyncio
async def test_search_btc(client):
    r = await client.get("/api/assets/search", params={"q": "btc"})
    assert r.status_code == 200
    assert any(x["symbol"] == "BTC" for x in r.json())


@pytest.mark.asyncio
async def test_quote_fallback(client):
    from app.backend.config import settings

    settings.enable_live_market_data = False
    r = await client.get("/api/assets/BTC", params={"asset_type": "crypto"})
    assert r.status_code == 200
    assert r.json()["source"] in ("live", "fallback")


@pytest.mark.asyncio
async def test_history_fallback(client):
    from app.backend.config import settings

    settings.enable_live_market_data = False
    r = await client.get("/api/assets/AAPL/history", params={"asset_type": "stock", "range": "7d"})
    assert r.status_code == 200
    assert len(r.json()["points"]) >= 7
