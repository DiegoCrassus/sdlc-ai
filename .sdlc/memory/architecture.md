# Architecture Memory

> Persistent architectural context for Cursor agents. Update when significant decisions are made.

## Current State

**Status:** Initialization — no application code exists yet.

## Boundaries

- `app/frontend/` — future web frontend (framework TBD)
- `app/backend/` — future API / service layer (Python, framework TBD)
- `app/infra/` — future infrastructure-as-code
- `app/shared/` — shared utilities and types

## Known Constraints

- Python is the primary backend language (inferred from pyproject.toml and `.env`)
- SQLite used for local development (`DATABASE_URL=sqlite+aiosqlite:///./data/rpg_op.db`)
- Production database: TBD (Supabase removed from scope)

## Design Principles

- Vertical slices over horizontal layers
- Small, reversible changes
- Observability from the start
- SDLC-driven development

## Open Questions

- Frontend framework not yet decided
- Deployment target (Kubernetes vs serverless) not yet decided
- Authentication strategy not yet decided
