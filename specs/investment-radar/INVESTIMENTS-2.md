# INVESTIMENTS-2 — Market Data

**GitHub:** #26 | **Branch:** `feature/INVESTIMENTS-2-issue-gh-26-market-data-fallback`

## Acceptance Criteria

1. `GET /api/assets/search?q=btc` returns ≥1 crypto result.
2. `GET /api/assets/BTC?asset_type=crypto` returns quote with `source` field.
3. `GET /api/assets/AAPL/history?asset_type=stock&range=7d` returns price points.
4. With `ENABLE_LIVE_MARKET_DATA=false`, endpoints still return fallback data.
5. `pytest app/backend/tests/test_market.py` passes.
