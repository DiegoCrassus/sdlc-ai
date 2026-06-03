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
| **Card** | INVES-88 |
| **Branch** | feature/INVES-88-studio-api-registry-s6 |
| **Stage** | implementation |

## Scope

Registry + validation API S5 (registry graph, validation inspect/run, doctor, simulation, assistance, skeleton).

## Deliverables

- `GET /studio/registry/graph` — registry graph + broken_refs from compile report
- `GET /studio/validation/inspect` — inspect-validation projection (query filters)
- `POST /studio/validation/run` — full validate result
- `POST /studio/doctor/run` — repo-root doctor subprocess
- `POST /studio/simulation/preview` — non-executing simulation
- `POST /studio/assistance/workflow` — advisory assistance
- `GET /studio/skeleton/tests` — MVP test skeleton list

## Verification (implementer)

```bash
STUDIO_REPO_ROOT=$(pwd) PYTHONPATH=app/studio-backend/src:$PWD python3 -m pytest app/studio-backend/tests/ -q
# 44 passed
```

## Blockers

None.

## Exact Next Action

QA: map acceptance criteria, run pytest + ruff, post evidence on Plane card.
