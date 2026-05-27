# Current State — Handoff

> **Updated:** 2026-05-27  
> **Branch:** `develop`  
> **Phase:** Investment Radar MVP implemented locally

## Summary

**Investment Radar** is a runnable financial monitoring demo: discover assets, watchlist, asset details with price history, and a simulated portfolio. Backend (FastAPI) + frontend (React/Vite) are implemented per Plane epic **INVES-19** (sub-tasks INVES-20..24).

This is **not a trading platform** — no real trades, brokerages, or payments.

## What works today

| Component | Status | Entry |
|-----------|--------|-------|
| Backend API | ✅ | `uvicorn app.backend.main:app --reload --port 8000` |
| Frontend SPA | ✅ | `cd app/frontend && npm run dev` |
| SQLite persistence | ✅ | `./data/investment_radar.db` |
| Market data + fallback | ✅ | `source: live \| fallback` on quotes |
| SDLC Doctor | ✅ | `make sdlc-doctor` |
| Observability | ✅ | `make obs-server` |

## Documentation

- **Local runbook:** [docs/product/investment-radar-runbook.md](../product/investment-radar-runbook.md)
- **API contract:** [docs/architecture/investment-radar-api.md](../architecture/investment-radar-api.md)
- **Architecture:** [docs/architecture/overview.md](../architecture/overview.md)

## Workflow (source of truth)

[docs/sdlc/change-lifecycle.md](../sdlc/change-lifecycle.md)

- Plane workspace: `investments-sdlc` · project: `investiments`
- Delivery: Plane card → feature branch → PR → CI green → merge `develop`

## Plane cards (Investment Radar)

| ID | Title | Status |
|----|-------|--------|
| INVES-19 | Product epic | In Progress |
| INVES-20 | Market data API | Done |
| INVES-21 | Watchlist API | Done |
| INVES-22 | Simulated portfolio | Done |
| INVES-23 | Frontend SPA | Done |
| INVES-24 | Runbook | Done (this update) |

## Next steps (optional)

- Production deployment ADR (auth, Postgres, hosting)
- `GET /api/v1/portfolio/summary` convenience endpoint
- OpenAPI → TypeScript codegen
- E2E tests (Playwright)
