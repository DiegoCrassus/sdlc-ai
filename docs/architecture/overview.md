# Architecture Overview

## Current Status

**Phase:** Investment Radar architecture defined — implementation pending (INVES-20..24).

The SDLC operating system is production-ready. **Investment Radar** is the first product vertical: a local demo for market data, watchlists, and simulated portfolios (no real trading).

## System Boundaries

```
sdlc-ai/
├── app/
│   ├── frontend/    ← React + Vite + TypeScript (INVES-23)
│   ├── backend/     ← FastAPI + SQLAlchemy async (INVES-20..22)
│   ├── infra/       ← Future infrastructure-as-code
│   └── shared/      ← Shared constants (optional JSON schemas)
├── .sdlc/           ← Machine-readable SDLC configuration
├── .cursor/         ← Cursor agent configuration
└── docs/            ← Human-readable documentation
```

## Investment Radar — Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser (localhost)                       │
│              React SPA — Vite dev server :5173                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST /api/v1/*
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (:8000)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Market data  │  │  Watchlist   │  │ Simulated portfolio  │ │
│  │ INVES-20     │  │  INVES-21    │  │ INVES-22             │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
│         │                 │                      │             │
│         ▼                 └──────────┬───────────┘             │
│  ┌──────────────┐                    ▼                          │
│  │ Provider     │           ┌─────────────────┐                  │
│  │ adapters +   │           │ SQLAlchemy async │                  │
│  │ fallback     │           │ SQLite (local)   │                  │
│  │ catalog      │           │ investment_radar │                  │
│  └──────┬───────┘           │ .db              │                  │
└─────────┼───────────────────┴─────────────────┴──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│              External market data (read-only)                    │
│   Finnhub · Alpha Vantage · CoinGecko · Brapi (optional)        │
└─────────────────────────────────────────────────────────────────┘
```

## App Boundaries Convention

- **frontend** — User interface layer. No business logic.
- **backend** — Business logic, API, data access. No rendering logic.
- **infra** — Infrastructure definitions (IaC, containers, cloud config).
- **shared** — Types, constants, and utilities shared between frontend and backend.

## Data Layer

- **Investment Radar (local):** SQLite `./data/investment_radar.db` via SQLAlchemy 2.0 async + aiosqlite
- **SDLC observability:** SQLite `.sdlc/obs/data/sdlc_obs.db` (separate concern)
- **Production target:** TBD — auth and hosted DB require future ADR

## Key Technology Decisions

| Area        | Decision                          | Status   | ADR / Doc                                      |
|-------------|-----------------------------------|----------|------------------------------------------------|
| Backend     | Python + FastAPI + Pydantic v2    | decided  | ADR-002, ADR-004                               |
| ASGI server | Uvicorn                           | decided  | ADR-004                                        |
| Database    | SQLite async (local MVP)          | decided  | ADR-003, ADR-007                               |
| ORM         | SQLAlchemy 2.0 async              | decided  | ADR-007                                        |
| Frontend    | React + Vite + TypeScript         | decided  | ADR-005                                        |
| Market data | Finnhub, Alpha Vantage, CoinGecko | decided  | ADR-006                                        |
| API contract| REST `/api/v1`, OpenAPI           | decided  | ADR-008, `investment-radar-api.md`             |
| Auth        | None (local single-user MVP)      | deferred | ADR-008                                        |
| Deployment  | Local demo only (INVES-24)        | pending  | Runbook sub-task                               |

## Design Principles

1. **Vertical slices** — Build full end-to-end features, not horizontal layers.
2. **Observability first** — Every component emits logs and metrics from day one.
3. **Small diffs** — Prefer reversible, scoped changes over large rewrites.
4. **SDLC-driven** — No code without a plan and acceptance criteria.
5. **Graceful degradation** — Live market data with explicit `source=fallback` when providers unavailable.

## Related Documents

- [System context](./system-context.md)
- [Architecture decisions](./decisions.md)
- [Investment Radar API contract](./investment-radar-api.md)
