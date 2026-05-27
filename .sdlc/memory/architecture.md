# Architecture Memory

> Persistent architectural context for Cursor agents. Update when significant decisions are made.

## Current State

**Status:** Investment Radar architecture complete (2026-05-27). Implementation not started — awaiting `start-change` per sub-task (INVES-20..24).

**Product:** Investment Radar — local demo for market data, watchlist, simulated portfolio. **Not a trading platform.**

## Confirmed Stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.12+, FastAPI, Pydantic v2, Uvicorn |
| Frontend | React 18+, Vite 5+, TypeScript |
| Database | SQLite `sqlite+aiosqlite:///./data/investment_radar.db` |
| ORM | SQLAlchemy 2.0 async |
| Market data | Finnhub (primary stocks), Alpha Vantage (secondary), CoinGecko (crypto), Brapi (optional B3), bundled fallback catalog |
| API | REST `/api/v1/*`, OpenAPI at `/api/v1/openapi.json` |
| Auth | None for MVP (single-user local) |

## Boundaries

- `app/frontend/` — React SPA; pages: search, watchlist, portfolio dashboard, asset detail/chart
- `app/backend/` — FastAPI routers: `health`, `assets`, `quotes`, `history`, `watchlist`, `portfolio`
- `app/infra/` — not in MVP scope
- `app/shared/` — optional shared constants; types primarily from OpenAPI duplication

## Domain Rules

- Asset ID format: `{class}:{symbol}` (e.g. `stock:AAPL`, `crypto:BTC`)
- All quotes expose `source: live | fallback`
- Simulated portfolio: seed `cash_balance` 100000 USD; transactions at current quote price
- Error JSON: `{ "error": { "code", "message", "details" } }`

## Plane Mapping

| Card | Scope |
|------|-------|
| INVES-19 | Epic — Investment Radar |
| INVES-20 | Market data service + fallback |
| INVES-21 | Watchlist API |
| INVES-22 | Simulated portfolio API |
| INVES-23 | Frontend web shell |
| INVES-24 | Local runbook / onboarding |

## Authoritative Docs

- API contract: `docs/architecture/investment-radar-api.md`
- ADRs: `docs/architecture/decisions.md` (ADR-001..008)
- Overview: `docs/architecture/overview.md`
- System context: `docs/architecture/system-context.md`

## Resolved Open Questions

- ~~Frontend framework~~ → React + Vite + TypeScript (ADR-005)
- ~~Backend framework~~ → FastAPI (ADR-004)
- ~~Market data providers~~ → Finnhub / Alpha Vantage / CoinGecko + fallback (ADR-006)
- ~~Auth~~ → Deferred for local MVP (ADR-008)
- ~~ORM~~ → SQLAlchemy async (ADR-007)

## Remaining Open Questions

- Production deployment target (Kubernetes vs serverless) — out of MVP scope
- Production database (Postgres/Supabase) — requires auth ADR first
- OpenAPI → TypeScript codegen — optional post-MVP
- Redis caching — env present but not used in MVP

## Design Principles

- Vertical slices over horizontal layers
- Small, reversible changes
- Observability from the start
- SDLC-driven development
- Graceful market data degradation with explicit provenance
