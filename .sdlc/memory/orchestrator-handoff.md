# Orchestrator Handoff (latest)

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | qa |
| **Stage complete** | yes |
| **Previous agent** | implementer |

## Session

| Field | Value |
|-------|-------|
| **Intent** | FEATURE |
| **Card** | INVES-79 |
| **Epic** | INVES-76 |
| **Branch** | feature/INVES-79-studio-ui-shell-s1 |
| **Stage** | implementation |

## Scope

Frontend S1 shell: Vite/React/Tailwind `app/studio-frontend`, hamburger nav + stubs, dashboard wired to `/studio/dashboard/summary`, health, readiness; `derived_non_authoritative` banners; `make studio-dev` runs API + UI.

## Acceptance criteria

- Vite + React + TypeScript + Tailwind on port 5174
- Top bar: repo label, gate chip from API, Open in Cursor link
- Hamburger sidebar with route stubs (Dashboard live)
- Dashboard fetches summary, readiness, health via Studio API
- Derived non-authoritative banners on dashboard and stubs
- `make studio-dev` starts backend and frontend
- Minimal vitest + optional smoke script

## Blockers

None.

## Notes

- **commits:** `45eaafb`
- **branch:** `feature/INVES-79-studio-ui-shell-s1`
- **Tests:** `cd app/studio-frontend && npm run test` — 3 passed; `npm run build` — OK; `npm run smoke` — OK (API on :8100)
- **Dev:** `make studio-dev` after `npm install` in `app/studio-frontend`
