# Orchestrator Handoff (latest)

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | qa |
| **Stage complete** | no |
| **Previous agent** | implementer |

## Session

| Field | Value |
|-------|-------|
| **Card** | INVES-108 |
| **Epic** | INVES-107 |
| **Branch** | `feature/INVES-108-watchlist-rebalance-api` |
| **Stage** | implementation |

## Implementation summary (INVES-108)

Per ADR-012:

- New ORM table `watchlist_invested_amounts` (`WatchlistInvestedAmountRow`) via `init_db()` / `create_all`
- `watchlist_rebalance.py` — pure Decimal rebalance math (weights, drift, suggestions, bands)
- `watchlist_allocations.py` — `list_invested`, `set_invested`, `invested_amount_to_cents`
- `domain/models.py` — `RebalanceSummary`, extended `WatchlistItem`, invested request/response types
- `PATCH /api/v1/watchlist/items/{symbol}/invested`
- GET watchlist + allocation PATCH responses enriched with rebalance fields + `rebalance_summary`
- Shared contract: `allocation.ts`, `allocation.schema.json`

## Commits

| Hash | Message |
|------|---------|
| `6028bc4` | `[INVES-108] Add watchlist rebalance API and persistence.` |

## Test evidence

```text
PYTHONPATH=app/backend/src python3 -m pytest app/backend/tests/test_watchlist.py app/backend/tests/test_watchlist_rebalance.py -v
21 passed in 0.70s
```

Coverage includes: jsonschema validation, zero-total null weights, balanced suggestions + penny tolerance, ROUND_HALF_UP rounding, drift bands (on_target/warning/off_target), invested persistence survives target clear.

## QA checklist

1. Run full backend test suite (`make -C app test-backend` or equivalent)
2. Validate jsonschema contract against live API responses
3. Map acceptance criteria on Plane card INVES-108 to test results
4. Contract-validator after merge (planner note)

## Blockers

None.

## Notes

- No Alembic in repo; table created via SQLAlchemy `create_all` (per architecture)
- INVES-109 (frontend) blocked until INVES-108 merged or contract frozen on branch
- Do not merge or open PR from QA — Reviewer → DevOps after QA pass
