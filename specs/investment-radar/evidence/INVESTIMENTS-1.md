# Evidence — INVESTIMENTS-1

| Field | Value |
|-------|-------|
| **Ticket** | INVESTIMENTS-1 |
| **GitHub** | #25 |
| **Branch** | `feature/INVESTIMENTS-1-issue-gh-25-backend-foundation` |
| **Stage** | implementation |
| **Agent** | implementer |

## Validation Output

```
$ .venv/bin/python -m pytest app/backend/tests/test_health.py -v
app/backend/tests/test_health.py::test_health_returns_ok PASSED [100%]
1 passed in 0.03s

$ .venv/bin/python -m ruff check app/backend
All checks passed!

$ make sdlc-doctor
Doctor summary: 94 passed, 0 warnings, 0 failed
```

## Acceptance Criteria

- [x] `GET /api/health` → 200 `{"status":"ok"}`
- [x] SQLite init on startup (`data/investment_radar.db`)
- [x] pytest health test passes
- [x] ruff check passes

## Files Changed

- `app/__init__.py`, `app/backend/*` (config, database, main, health router, tests)
- `pyproject.toml` (FastAPI deps)
