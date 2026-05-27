# Architecture: Investment Radar

> **Stage:** Architecture (INVESTIMENTS-0)  
> **ADR:** ADR-005 (proposed below)

## System Context

```
┌─────────────┐     HTTP      ┌──────────────────┐
│  React SPA  │ ────────────► │  FastAPI :8000   │
│  :5173      │               │  app/backend     │
└─────────────┘               └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
              SQLite (local)    CoinGecko API      yfinance
              watchlist         (crypto)           (stocks)
              portfolio                            │
              alerts                               ▼
                                            fallback_catalog
```

## Boundaries

| Layer | Path | Responsibility |
|-------|------|----------------|
| API | `app/backend/routers/` | HTTP routes, validation |
| Services | `app/backend/services/` | Market data, enrichment |
| Persistence | `app/backend/models.py` | SQLAlchemy models |
| UI | `app/frontend/src/` | Pages, components, API client |

## Data Sources

1. **Live:** CoinGecko REST (no key), yfinance (stocks)
2. **Fallback:** `fallback_catalog.py` — curated symbols + synthetic history
3. **Transparency:** Every quote includes `source: live | fallback`

## ADR-005 — Investment Radar Stack

- **Date:** 2026-05-27
- **Status:** accepted (this epic)
- **Decision:** FastAPI + SQLAlchemy async SQLite + React Vite TS + Tailwind
- **Consequences:** `pyproject.toml` gains app deps; CI may add pytest job later

## Impacted Areas

```
app/backend/          ← new package
app/frontend/         ← new Vite app
specs/investment-radar/
docs/handoff/current-state.md
Makefile
pyproject.toml
README.md
```
