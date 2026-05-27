# app/shared

## Purpose

Shared utilities, types, and constants used by both frontend and backend.

## Status

**Not yet implemented.** This boundary is reserved for cross-cutting concerns.

## What Belongs Here

- Shared type definitions (e.g., Pydantic models or JSON Schema)
- Shared constants and enumerations
- Shared utility functions with no side effects
- API contract definitions (OpenAPI spec if shared)
- Serialization/deserialization helpers

## What Does NOT Belong Here

- Frontend-specific code — goes in `app/frontend/`
- Backend-specific code — goes in `app/backend/`
- Infrastructure — goes in `app/infra/`
- Business logic — goes in `app/backend/`

## When to Add Code Here

Add code to `app/shared/` only when:
1. It is used by both frontend and backend.
2. It has no side effects (pure functions or data definitions).
3. It would otherwise be duplicated.

Do not add code "just in case" it might be shared later.

## Expected Future Structure

```
app/shared/
├── types/              ← Shared type definitions
├── constants/          ← Shared constants and enumerations
├── utils/              ← Shared pure utility functions
└── README.md           ← (this file, extended)
```

## Setup (When Implemented)

TBD. If Python-only, this will be a package installed as a dependency by backend (and potentially compiled/bundled for frontend use).
