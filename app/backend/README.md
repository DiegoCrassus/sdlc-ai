# app/backend

## Purpose

Python backend service for the sdlc-ai project. Contains business logic, API layer, and data access.

## Status

**Not yet implemented.** This boundary is reserved for the Python service.

## What Belongs Here

- API endpoints (REST or GraphQL)
- Business logic and domain models
- Database models and migrations
- Background tasks and jobs
- Authentication and authorization logic
- Backend-specific configuration

## What Does NOT Belong Here

- UI rendering — goes in `app/frontend/`
- Infrastructure definitions — goes in `app/infra/`
- Shared types used by both frontend and backend — goes in `app/shared/`
- SDLC configuration — goes in `.sdlc/`

## Expected Future Structure

```
app/backend/
├── src/
│   ├── api/            ← API routes and handlers
│   ├── core/           ← Business logic and domain models
│   ├── db/             ← Database models, sessions, migrations
│   ├── services/       ← External service integrations
│   └── config.py       ← Configuration from env vars
├── tests/
│   ├── unit/
│   └── integration/
├── migrations/         ← Database migration files (Alembic)
└── README.md
```

## Technology

- **Language:** Python 3.11+
- **Database:** SQLite (local), Supabase/PostgreSQL (production)
- **ORM:** TBD (likely SQLAlchemy with async)
- **Framework:** TBD (FastAPI is a likely candidate)
- **Tests:** pytest

## Setup (When Implemented)

Follow `docs/sdlc/change-lifecycle.md` before any implementation.

```bash
pip install -e ".[dev]"
python -m pytest app/backend/tests/ -v
```
