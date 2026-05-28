# SDLC Memory — Context Management Protocol

> All files in this directory are agent-writable runtime state.
> They are excluded from git history where sensitive, or committed as SDLC evidence where required.

## Files

| File | Purpose | Written by | Read by |
|------|---------|-----------|---------|
| `operational-context.md` | Environment, services, Plane project | DevOps, Orchestrator | All agents |
| `architecture.md` | Current system boundaries and ADR summary | Architect | Implementer, Reviewer |
| `business-rules.md` | Domain invariants and non-negotiable constraints | Planner | All agents |
| `incidents.md` | Production incident log | Observer, DevOps | AutoFixer, Rollback |
| `discovery-context.json` | Latest repo discovery snapshot | `discovery_hook.py` | Intent Analyst, Planner |
| `orchestrator-handoff.md` | Intent classification result and next step | Intent Analyst | Orchestrator |
| `session-gate.json` | Current session state (card, branch, stage, agent) | `gate.py` CLI | All agents, sdlc_gate_hook |
| `test-skeleton.md` | Test stubs generated during requirements stage | QA (skeleton mode) | Implementer, QA |

---

## Context Window Budget (per stage)

Agents must respect token budgets defined in `.sdlc/stages.yaml` (`context_budget_tokens`).
When a session exceeds the budget, apply the compaction protocol below.

| Stage | Budget |
|-------|--------|
| ticket | 8 000 tokens |
| requirements | 16 000 tokens |
| architecture | 24 000 tokens |
| implementation | 40 000 tokens |
| validation | 20 000 tokens |
| review | 20 000 tokens |
| deployment | 16 000 tokens |
| observability | 12 000 tokens |
| incident | 16 000 tokens |
| autofix | 24 000 tokens |

---

## Rolling-Summary Protocol

When a session approaches its context budget:

1. **Pause** before the next action.
2. **Write a compact summary** of the session so far to `operational-context.md`:
   ```markdown
   ## Session summary — <ISO timestamp>
   Stage: <stage>
   Card: <INVES-N>
   Branch: <branch>
   Completed: <bullet list of what was done>
   In progress: <current action>
   Next: <immediate next step>
   ```
3. **Discard** in-context tool outputs that are no longer needed (only the summary survives).
4. **Continue** with fresh context loaded from the summary and relevant files only.

Run `make sdlc-compact-memory` to trigger this automatically via a helper script.

---

## Compaction Script

```bash
make sdlc-compact-memory
# Reads: .sdlc/memory/operational-context.md + session-gate.json
# Writes: .sdlc/memory/operational-context.md (appends compact summary block)
# Effect: truncates stale sections while preserving the last N summaries
```

---

## Cross-Session Resume Protocol

Before starting any new turn:

1. Read `session-gate.json` — if `gate_status: open`, **resume** the existing session.
2. Load `orchestrator-handoff.md` — if present, apply the `next_agent` directive.
3. Load `operational-context.md` — last summary block only (not full history).
4. Load `discovery-context.json` — latest repo state snapshot.

This ensures context continuity across IDE restarts and long-running tasks.
