# INVESTIMENTS-1 — Backend Foundation

**GitHub:** #25 | **Branch:** `feature/INVESTIMENTS-1-issue-gh-25-backend-foundation`

## Acceptance Criteria

1. `GET /api/health` returns `200` with `{"status":"ok"}`.
2. SQLite DB initializes on startup at `data/investment_radar.db`.
3. `python -m pytest app/backend/tests/test_health.py` passes.
4. `ruff check app/backend` exits 0.

## DoD

- [ ] Tests pass
- [ ] `make sdlc-doctor` exits 0
- [ ] Evidence in `evidence/INVESTIMENTS-1.md`
