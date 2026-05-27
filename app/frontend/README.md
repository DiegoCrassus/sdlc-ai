# app/frontend

## Purpose

Web frontend for the sdlc-ai project.

## Status

**Not yet implemented.** This boundary is reserved for the future web UI.

## What Belongs Here

- UI components and pages
- Frontend routing
- Client-side state management
- Styles and assets
- Frontend-specific configuration (build, lint, format)
- Frontend tests

## What Does NOT Belong Here

- Business logic — goes in `app/backend/`
- Database access — goes in `app/backend/`
- Shared types used by both frontend and backend — goes in `app/shared/`
- Infrastructure definitions — goes in `app/infra/`
- API definitions — goes in `app/backend/`

## Expected Future Structure

```
app/frontend/
├── src/
│   ├── components/     ← Reusable UI components
│   ├── pages/          ← Page-level components
│   ├── hooks/          ← Custom React hooks (if React)
│   ├── store/          ← Client state (if needed)
│   └── api/            ← API client calls
├── public/             ← Static assets
├── tests/              ← Frontend unit and E2E tests
├── package.json
└── README.md           ← (this file, extended with setup instructions)
```

## Framework Decision

**TBD** — Framework will be decided when frontend development begins.
An ADR will be written in `docs/architecture/decisions.md` at that time.

## Setup (When Implemented)

TBD.
