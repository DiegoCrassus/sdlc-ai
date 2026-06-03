# Architecture Memory

> Persistent architectural context for Cursor agents. Update when significant decisions are made.

## Current State

**Status:** Dual product surface in `app/` — MarketPulse (financial dashboard) + Studio Service (SDLC control plane, architecture complete INVES-77).

| Package | Purpose | Status |
|---------|---------|--------|
| `app/backend/` | MarketPulse API (`marketpulse`) | Implemented |
| `app/frontend/` | MarketPulse UI | Implemented |
| `app/studio-backend/` | Studio Service API (`studio_service`) | Architecture only — INVES-78 |
| `app/studio-frontend/` | Studio Service UI | Architecture only — INVES-79 |
| `app/infra/sdlc_obs/` | SDLC metrics SQLite + dashboard | Implemented |
| `studio/` | Foundation engine (compile, validate, canvas) | Implemented (S0) |
| `app/shared/` | Cross-product JSON schemas / TS types | MarketPulse-focused |

## Studio Service boundaries (INVES-77)

- **Doc:** `docs/architecture/studio-service-platform.md`
- **ADR:** ADR-009 in `docs/architecture/decisions.md`
- API prefix `/studio/*`, ports 8100 (API) + 5174 (UI)
- Mutations: propose → review → git/Plane apply (no silent writes)
- Observability: `StudioEvent` envelope over SSE; sources = sdlc_obs + gateway hooks + handoff + gate
- React Flow: renders derived canvas; layout is UI-local only

## MarketPulse boundaries

- `app/backend/src/marketpulse/` — FastAPI, `/api/v1/*`, port 8000
- `app/frontend/` — Vite SPA, port 5173
- ADRs: ADR-004..008, `docs/architecture/marketpulse-api-providers.md`

## Known Constraints

- Python primary backend language
- SQLite for local dev (product DB + sdlc_obs)
- Plane + GitHub MCP for workflow
- Studio never bypasses `.cursor/hooks` write gate

## Open Questions

- pyproject packaging for `studio_service` — optional `[studio]` extra vs dedicated editable install (INVES-78)
- `sdlc_events` SQLite table vs JSONL for gateway events (S3 — prefer table for timeline queries)

## Design Principles

- Vertical slices over horizontal layers
- Small, reversible changes
- Observability from the start
- SDLC-driven development
- Derived views labeled; authoritative sources unchanged
