# app/shared

## Purpose

Shared utilities, types, and constants used by both frontend and backend.

## Status

**Implemented (INVES-35):** Forecast projection JSON Schema + TypeScript types for `GET /api/v1/projections/{symbol}`.

**Implemented (INVES-37):** Auth identity JSON Schema + TypeScript types for email-only session API (ADR-010).

## Structure

```
app/shared/
├── contracts/
│   ├── forecast.schema.json   ← Canonical AssetProjection JSON Schema (ADR-009)
│   └── auth.schema.json       ← User, Identify*, AuthMeResponse, SessionError (ADR-010)
├── types/
│   ├── forecast.ts            ← TypeScript mirror for frontend (@shared alias)
│   └── auth.ts                ← TypeScript mirror + session cookie constants
└── README.md
```

## Forecast contract (INVES-35)

See `contracts/forecast.schema.json` and `types/forecast.ts` for projection types used by market data endpoints.

## Auth contract (INVES-37)

| Type | Use |
|------|-----|
| `User` | `{ id, email }` in success bodies |
| `IdentifyRequest` | POST `/api/v1/auth/identify` body |
| `IdentifyResponse` | Identify success JSON (cookie `mp_session` via Set-Cookie) |
| `AuthMeResponse` | GET `/api/v1/auth/me` success JSON |
| `SessionError` | 401 / 422 error envelope |

Session: **HttpOnly cookie** `mp_session` — not Bearer. Frontend uses `credentials: "include"`.

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

Vite alias `@shared` → `app/shared` (see `app/frontend/vite.config.ts`). Re-export from `app/frontend/src/types/market.ts` for backward-compatible forecast imports.

```ts
import type { User, IdentifyRequest } from "@shared/types/auth";
```
