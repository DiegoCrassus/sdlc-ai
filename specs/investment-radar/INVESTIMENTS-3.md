# INVESTIMENTS-3 — User Data APIs

**GitHub:** #27 | **Branch:** `feature/INVESTIMENTS-3-issue-gh-27-user-data-apis`

## Acceptance Criteria

1. CRUD watchlist: `GET/POST/DELETE /api/watchlist`.
2. CRUD portfolio: `GET/POST/PATCH/DELETE /api/portfolio/positions`, `GET /api/portfolio/summary`.
3. CRUD alerts: `GET/POST/DELETE /api/alerts`, `POST /api/alerts/check`.
4. `GET /api/meta/sources` returns provider status.
5. `pytest app/backend/tests/test_user_data.py` passes.
