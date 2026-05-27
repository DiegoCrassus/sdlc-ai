# AI-Native SDLC Guide

## What is AI-Native SDLC?

AI-Native SDLC is a software development lifecycle model designed for teams where AI agents operate as first-class participants alongside human developers.

Unlike traditional SDLC models, AI-Native SDLC:
- Treats agents as specialized team members with defined roles, inputs, and outputs.
- Makes every stage explicit and machine-readable (YAML configuration).
- Enforces deterministic gates before stage transitions.
- Requires evidence — not claims — to advance.
- Maintains persistent memory so agents can operate with continuity across sessions.

## The 10-Stage Lifecycle

```
1. Ticket      → Capture intent and acceptance criteria
2. Requirements → Refine scope, risks, non-goals
3. Architecture → Define technical approach and boundaries
4. Implementation → Implement in focused, reversible diffs
5. Validation  → Verify with real test evidence
6. PR & Review → Review correctness, security, maintainability
7. Deployment  → Release safely with rollback plan
8. Observability → Confirm signals: logs, metrics, traces
9. Incident    → Diagnose, mitigate, and post-mortem
10. Auto Fix   → Prepare corrective changes from evidence
```

## How Agents Operate

Each stage has:
- **Inputs** — What the agent must load before acting
- **Outputs** — What the agent must produce
- **Required evidence** — What must exist before the stage is considered complete
- **Gates** — Conditions that must be true before transitioning to the next stage

Agents are specialized (see `.cursor/subagents/`):
- **Planner** — Ticket and requirements
- **Architect** — Architecture
- **Implementer** — Implementation and auto-fix
- **QA** — Validation
- **Reviewer** — PR & Review
- **DevOps** — Deployment and observability
- **Doctor** — Cross-stage validation

## Context Loading Protocol

Before any major task, an agent must:
1. Read `.sdlc/sdlc.yaml`
2. Read `.sdlc/memory/architecture.md`
3. Read `.sdlc/memory/business-rules.md`
4. Read relevant docs for the current stage
5. Identify the current lifecycle stage

## Governance Rules

Key rules (full list in `.sdlc/rules.yaml`):

| Rule | Severity |
|------|----------|
| No fake validation | required |
| Docs sync required | required |
| Doctor after structural change | required |
| Small diffs preferred | warning |
| Explicit assumptions required | required |
| Handoff before major transition | required |

## The Doctor

The Doctor is the repository health check. It validates:
- All required directories and files exist
- All YAML files parse correctly
- Cursor configuration is complete
- Docs are non-empty
- Makefile targets exist

Run: `make sdlc-doctor`

The Doctor must pass (exit 0) after any structural change.
Never modify Doctor rules to hide real failures.

## Human in the Loop

Agents operate autonomously within their defined scope but escalate when:
- A decision has significant security implications
- A change affects multiple systems or teams
- Acceptance criteria are disputed
- Auto-fix results require merge approval

Human review is always required before merging auto-fix changes.
