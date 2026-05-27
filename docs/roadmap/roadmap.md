# Roadmap

## Current Phase: Foundation

**Status:** SDLC operating system initialized. No application code yet.

## Phase 1 — Foundation (current)

| Item | Status | Notes |
|------|--------|-------|
| SDLC YAML configuration | done | `.sdlc/*.yaml` |
| Python DSL and Doctor | done | `.sdlc/dsl/` |
| Cursor agent configuration | done | `.cursor/` |
| Documentation structure | done | `docs/` |
| App boundary definitions | done | `app/*/README.md` |

## Phase 2 — Backend Foundation (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Python project structure | pending | `app/backend/` |
| Database models | pending | SQLAlchemy + SQLite/Supabase |
| API framework setup | pending | Framework TBD |
| First API endpoint | pending | Depends on product definition |
| Unit test setup | pending | pytest |
| CI/CD pipeline | pending | GitHub Actions |

## Phase 3 — Frontend Foundation (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Frontend framework decision | pending | ADR needed |
| Project scaffold | pending | `app/frontend/` |
| Design system decision | pending | TBD |
| First UI component | pending | Depends on product definition |

## Phase 4 — Infrastructure (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Docker setup | pending | `app/infra/` |
| CI/CD deployment | pending | GitHub Actions |
| Staging environment | pending | TBD |
| Production deployment | pending | TBD |

## Milestones

| Milestone | Target | Criteria |
|-----------|--------|----------|
| SDLC Foundation | 2026-05-26 | Doctor passes, all config in place |
| First Backend Service | TBD | API running locally with tests |
| First E2E Feature | TBD | Frontend + backend + tests + deployed |
| Production Ready | TBD | Monitoring, rollback, and runbook complete |

## Backlog (Unscheduled)

- Auth system
- User management
- Observability stack (OpenTelemetry + Sentry)
- Admin tooling
- Multi-environment deployment

---

*Update this file at each phase transition. Keep it honest — no aspirational dates without commitment.*
