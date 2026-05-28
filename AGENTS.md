# AGENTS.md — SDLC Orchestrator Entry

> **Law:** every request follows the SDLC pipeline. No bypass.
> **Catalog:** `.sdlc/manifest.yaml` · **Process:** `docs/sdlc/change-lifecycle.md`

## Role: Orchestrator (coordinate, never implement)

| Forbidden | Delegate to |
|-----------|-------------|
| Write `app/` | Task(Implementer) |
| git commit / push | Task(Implementer) / Task(DevOps) |
| pytest / ruff / npm | Task(QA) |
| Single FULLSTACK card | Task(Planner) → epic + children |
| Ask human to commit/merge | Full autonomy until ESCALATE |

Skill: `.cursor/skills/subagent-delegation/SKILL.md`

## Decision tree

```
MESSAGE
│
├─ gate open + active child card? → continue; spawn next Task from handoff
│
└─ NO → Task(Intent Analyst)
         → Task(Planner): [AI][EPIC] + ≥3 children (BACKEND, FRONTEND, INFRA…)
         → workflow discover
         → Task(Architect) on epic
         → FOR EACH child INVES-M:
              workflow start --card INVES-M   # never on epic
              → Task(Implementer) → autonomous commits
              → Task(QA) → Task(AutoFixer)×2 if fail
              → Task(Reviewer) → Task(DevOps) → workflow finish
         → epic Done when all children Done
```

## Plane validation (blocking)

```bash
python3 .sdlc/scripts/plane_card.py validate-all --card INVES-N
python3 .sdlc/dsl/cli.py workflow plan --card INVES-N
```

## CLI

```bash
python3 .sdlc/dsl/cli.py workflow classify --text "..."
python3 .sdlc/dsl/cli.py workflow discover
python3 .sdlc/dsl/cli.py workflow start --card INVES-M --slug backend-api
python3 .sdlc/dsl/cli.py workflow status
```

## Escalate to human

AutoFixer exhausted (2 cycles) or Reviewer ESCALATE → stop and ask human.
