# SDLC Handbook — Agents, Skills, and References

> **Not the entry point.** Read **[`AGENTS.md` at the repo root](../AGENTS.md)** first (L0 manifest — decision tree).  
> This file (`.sdlc/HANDBOOK.md`) is the **reference handbook** (catalog of subagents, skills, MCPs, conventions).

## Documentation layers

| Layer | File | Role |
|--------|---------|--------|
| **L0 — Manifest** | [`AGENTS.md`](../AGENTS.md) (root) | Decision tree, Orchestrator, CLI — ~1 page |
| **Handbook** | `.sdlc/HANDBOOK.md` (this file) | Detailed catalog and conventions |
| **Process** | `docs/sdlc/master-workflow.md` | Approved P0/P1 flow |
| **Gitflow** | `docs/sdlc/change-lifecycle.md` | Plane, branch, merge — authority |

**Human guide:** [`SDLC-GUIDE.md`](../SDLC-GUIDE.md) · **Deep dive (papers + behavior):** [`SDLC-DEEP-DIVE.md`](../SDLC-DEEP-DIVE.md)

## SDLC law (anti-bypass)

- Rules: `001-sdlc-anti-bypass.mdc`, `002-sdlc-orchestrator-principal.mdc`, `003-orchestrator-delegation-only.mdc`
- Plane granularity: `.sdlc/plane-granularity.yaml` — epic + children; monolithic `[AI][FULLSTACK]` forbidden
- Delegation: `.cursor/skills/subagent-delegation/SKILL.md`
- Gate: `python3 .sdlc/dsl/cli.py workflow status`

## Project identity

- **Repository:** `sdlc-ai`
- **Plane workspace:** `investments-sdlc` → `PLANE_WORKSPACE_SLUG`
- **Plane project:** `investiments` → `PLANE_PROJECT_NAME`
- **Cards:** `INVES-N`
- **GitHub:** see `.env` → `GITHUB_REPOSITORY`
- **SDLC version:** v2.0 (P0 + P1)

## Reading order (agent)

```
1. AGENTS.md (root)              ← L0 manifest — required first
2. docs/sdlc/master-workflow.md  ← full process
3. docs/sdlc/change-lifecycle.md ← gitflow + Plane
4. .sdlc/HANDBOOK.md             ← catalog when you need reference
5. .sdlc/memory/operational-context.md
6. Skill/subagent for current stage
```

## Subagents

| Agent | File | Role |
|--------|---------|-------|
| **Intent Analyst** | `.cursor/subagents/intent-analyst.md` | Classifies request — **always first** (via Task) |
| Planner | `.cursor/subagents/planner.md` | Epic + children on Plane |
| Architect | `.cursor/subagents/architect.md` | Architecture notes on Plane |
| Implementer | `.cursor/subagents/implementer.md` | Code + autonomous commits |
| QA | `.cursor/subagents/qa.md` | Lint, tests, doctor |
| Reviewer | `.cursor/subagents/reviewer.md` | APPROVE \| ESCALATE |
| DevOps | `.cursor/subagents/devops.md` | Push, PR, merge |
| AutoFixer | `.cursor/subagents/auto-fixer.md` | Fixes CI/lint failures (max 2 cycles) |
| Doctor | `.cursor/subagents/doctor.md` | Structural validation |
| Observer | `.cursor/subagents/observer.md` | Observability metrics |
| IssueAnalyst | `.cursor/subagents/issue-analyst.md` | GitHub Issues triage |
| SDLCAuditor | `.cursor/subagents/sdlc-auditor.md` | Autonomous audit |
| MigrationRunner | `.cursor/subagents/migration-runner.md` | Migrations |
| ContractValidator | `.cursor/subagents/contract-validator.md` | OpenAPI ↔ TS |
| RollbackAgent | `.cursor/subagents/rollback-agent.md` | Rollback |
| SecurityScanner | `.cursor/subagents/security-scanner.md` | SAST/secrets |

## Critical skills (P0/P1)

| Skill | Path | When |
|-------|------|--------|
| Orchestrator | `sdlc-orchestrator/SKILL.md` | Task coordination |
| Subagent delegation | `subagent-delegation/SKILL.md` | Orchestrator → Task matrix |
| Plane task creation | `plane-task-creation/SKILL.md` | Epic + children |
| Plane SDLC | `plane-sdlc/SKILL.md` | Plane MCP |
| Intent classification | `intent-classification/SKILL.md` | Classify intent |
| QA checklist | `qa-minimum-checklist/SKILL.md` | Minimum validation |
| Start / finish change | `start-change/`, `finish-change/` | Branch + merge |
| Branch naming | `branch-naming.md` | `feature/INVES-N-<slug>` |

Other skills in `.cursor/skills/` (implementation, qa-validation, auto-merge-policy, etc.).

## Cursor commands

| Command | Purpose |
|---------|-----------|
| `/sdlc-plan` | Plan [AI][TYPE] |
| `/sdlc-implement` | Implementation |
| `/sdlc-review` | PR review |
| `/sdlc-doctor` | Doctor |
| `/sdlc-audit` | Audit + canvas |
| `/sdlc-handoff` | Handoff summary |

## Conventions

- **Task names:** `[AI][EPIC|BACKEND|FRONTEND|INFRA|…] Short title`
- **Branch:** `feature/INVES-N-<slug>` (or `bugfix/`, `sdlc/`, etc.)
- **Before coding in `app/`:** `workflow start --card INVES-M` (child, never epic)
- **Before merge:** green CI + Reviewer APPROVE + `finish-change`
- **After structural change:** `make sdlc-doctor`

## MCPs

- **Plane MCP:** work items, evidence, Done — skill `plane-sdlc`
- **GitHub MCP:** PRs, merge — skill `github-sdlc`

## Prohibitions

- Never a `specs/` folder or local tickets/evidence
- Orchestrator never implements/commits/lints directly

## Makefile (reference)

```bash
make sdlc-doctor
make workflow-status
make workflow-start CARD=INVES-N SLUG=... STAGE=implementation
make workflow-discover
make sdlc-audit
make obs-server
```

## Escalate to human

Only when:

1. AutoFixer exhausted 2 cycles and QA still fails
2. Reviewer returns **ESCALATE**
3. External blocker (Plane/GitHub/API unavailable)
4. Product decision outside card scope

Otherwise: autonomous pipeline (commit, push, merge without asking human).

## Repository state (product)

`app/backend/` and `app/frontend/` — **placeholders** until next greenfield delivery via full workflow.

For current Doctor/Audit scores: run `make sdlc-doctor` and `make sdlc-audit` (do not trust fixed numbers in this doc).
