# Architecture Memory

> Persistent architectural context for Cursor agents. Update when significant decisions are made.

## Current State

**Status:** App reset (2026-05-27) — `app/backend/` and `app/frontend/` are placeholders. No product code in tree.

**Retest:** Full SDLC greenfield cycle can be run again from a new agent session.

## Boundaries

- `app/frontend/` — placeholder (future web UI)
- `app/backend/` — placeholder (future API)
- `app/infra/` — SDLC observability (`sdlc_obs/`) + terraform placeholders
- `app/shared/` — placeholder

## Reference architecture (prior cycle — docs only)

Investment Radar was delivered once (INVES-19..24). Authoritative specs remain in:

- `docs/architecture/investment-radar-api.md`
- `docs/architecture/decisions.md` (ADR-004..008)
- `docs/architecture/overview.md`

Re-implementation should follow those ADRs unless a new ADR supersedes them.

## Known Constraints

- Python primary backend language
- SQLite for local dev when product returns
- Plane + GitHub MCP for workflow

## Open Questions

- Reuse INVES-19 epic vs new Plane epic for retest (Orchestrator/Planner decision)
- Frontend/backend re-implementation order unchanged: market → watchlist → portfolio → UI → docs

## Design Principles

- Vertical slices over horizontal layers
- Small, reversible changes
- Observability from the start
- SDLC-driven development
