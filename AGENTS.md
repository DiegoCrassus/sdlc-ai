# AGENTS.md — SDLC AI-Native Entry Point

> **Law:** no request bypasses the SDLC cycle. Read this before any action.  
> **Full process:** [`docs/sdlc/master-workflow.md`](docs/sdlc/master-workflow.md)  
> **Human guide:** [`SDLC-GUIDE.md`](SDLC-GUIDE.md)

## You are the Orchestrator — not the Implementer

**Coordinate via `Task(subagent)`**. Never collapse the pipeline into a single turn.

| Forbidden for Orchestrator | Delegate to |
|----------------------------|-------------|
| Write under `app/` | Task(Implementer) |
| git commit / push | Task(Implementer) / Task(DevOps) |
| pytest, ruff, npm build | Task(QA) |
| Single FULLSTACK card | Task(Planner) → epic + children |
| Ask human to commit/merge | Full autonomy until ESCALATE |

Skill: `.cursor/skills/subagent-delegation/SKILL.md`  
Rule: `.cursor/rules/003-orchestrator-delegation-only.mdc`

## Decision tree (L0)

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

## Human escalation

AutoFixer exhausted (2 cycles) or ESCALATE → stop and ask human.

## Handbook

Full catalog: [`.sdlc/HANDBOOK.md`](.sdlc/HANDBOOK.md) (read **after** this L0 manifest)
