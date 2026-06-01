# app/shared

## Purpose

Shared utilities, types, and constants used by both frontend and backend.

## Status

**Implemented (INVES-35):** Forecast projection JSON Schema + TypeScript types for `GET /api/v1/projections/{symbol}`.

**Implemented (INVES-37):** Auth identity JSON Schema + TypeScript types for email-only session API (ADR-010).

**Implemented (INVES-42):** Price alert JSON Schema + TypeScript types for watchlist alert CRUD API (ADR-011).

**Implemented (INVES-48):** Watchlist allocation target/status JSON Schema + TypeScript types.

## Structure

```
app/shared/
├── contracts/
│   ├── forecast.schema.json   ← Canonical AssetProjection JSON Schema (ADR-009)
│   ├── auth.schema.json       ← User, Identify*, AuthMeResponse, SessionError (ADR-010)
│   ├── alerts.schema.json     ← PriceAlert, CreateAlertRequest, AlertListResponse (ADR-011)
│   └── allocation.schema.json ← Watchlist allocation target/status contract
├── types/
│   ├── forecast.ts            ← TypeScript mirror for frontend (@shared alias)
│   ├── auth.ts                ← TypeScript mirror + session cookie constants
│   ├── alerts.ts              ← TypeScript mirror + ALERTS_API_PATHS
│   └── allocation.ts          ← TypeScript mirror + WATCHLIST_API_PATHS
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

## Alerts contract (INVES-42)

| Type | Use |
|------|-----|
| `PriceAlert` | `{ id, symbol, direction, target_price, triggered_at, created_at }` |
| `CreateAlertRequest` | POST `/api/v1/alerts` body |
| `AlertListResponse` | GET `/api/v1/alerts` success JSON `{ items: PriceAlert[] }` |
| `AlertError` | 400 / 404 error envelope |

Paths: `ALERTS_API_PATHS.list`, `ALERTS_API_PATHS.detail(alertId)`.

## Watchlist allocation contract (INVES-48)

| Type | Use |
|------|-----|
| `AllocationStatus` | `"under_allocated"`, `"balanced"`, or `"over_allocated"` summary status |
| `WatchlistItem` | Existing watchlist row plus optional/nullable `target_percent` |
| `WatchlistAllocationSummary` | Overall `{ target_percent_total, status }` |
| `WatchlistResponse` | GET `/api/v1/watchlist` success JSON `{ items, allocation_summary }` |
| `UpdateWatchlistAllocationRequest` | PATCH body `{ target_percent: number | null }`; `null` clears the target |
| `UpdateWatchlistAllocationResponse` | PATCH success JSON `{ item, allocation_summary }` |

Paths: `WATCHLIST_API_PATHS.list`, `WATCHLIST_API_PATHS.itemAllocation(symbol)`.

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
import type { PriceAlert, CreateAlertRequest } from "@shared/types/alerts";
import type { WatchlistResponse, UpdateWatchlistAllocationRequest } from "@shared/types/allocation";
```
