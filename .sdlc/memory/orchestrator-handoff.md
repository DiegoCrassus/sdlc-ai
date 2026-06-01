# Orchestrator Handoff (latest)

```yaml
agent: auto-fixer
card: INVES-43
stage_complete: false
next_agent: qa
branch: feature/INVES-43-backend-alerts-api
epic: INVES-41
attempt: 1

fixes_applied:
  - rule: I001
    files:
      - app/backend/src/marketpulse/domain/models.py
      - app/backend/tests/conftest.py
      - app/backend/tests/test_alerts.py
    action: ruff check --fix (import sort)
  - rule: B008
    file: app/backend/src/marketpulse/api/v1/routes/watchlist.py
    action: >
      Refactored Depends() default to Annotated[MarketDataProvider, Depends(...)]
      matching alerts.py FastAPI DI pattern.

local_verification:
  ruff_check: "All checks passed (4 files)"
  pytest_alerts: pending_qa_rerun

commit: "[INVES-43] fix: resolve ruff I001 and B008 lint failures"

next_steps: >
  Task(QA) re-run full checklist on INVES-43 — lint (step 4) should now PASS;
  confirm product tests and AC mapping unchanged.
```
