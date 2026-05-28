# app/shared

## Purpose

Shared utilities, types, and constants used by both frontend and backend.

## Status

**Implemented (INVES-35):** Forecast projection JSON Schema + TypeScript types for `GET /api/v1/projections/{symbol}`.

## Structure

```
app/shared/
├── contracts/
│   └── forecast.schema.json   ← Canonical AssetProjection JSON Schema (ADR-009)
├── types/
│   └── forecast.ts            ← TypeScript mirror for frontend (@shared alias)
└── README.md
```

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

## Frontend import

Vite alias `@shared` → `app/shared` (see `app/frontend/vite.config.ts`). Re-export from `app/frontend/src/types/market.ts` for backward-compatible imports.
