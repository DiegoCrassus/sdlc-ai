# Skill: SDLC Orchestrator

> **Authority:** `docs/sdlc/master-workflow.md` · `003-orchestrator-delegation-only.mdc`

## Purpose

Orchestrator Principal: **spawn Tasks, read handoffs, spawn next Task**. Never implement, commit, lint, or test directly.

## Anti-pattern (MarketPulse lesson)

```
WRONG: Orchestrator → WebSearch → Write app/ → single FULLSTACK card
RIGHT: Task(Intent) → Task(Planner) epic+3 children → per child: Task(Impl)→Task(QA)→Task(Review)
```

## Plane granularity

| Intent | Plane structure |
|--------|-----------------|
| GREENFIELD | 1 epic + ≥3 child cards |
| FEATURE | 1 epic + ≥2 child cards |
| BUGFIX/HOTFIX | 1 card OK |

Validate: `plane_card.py validate-all --card INVES-N`

## Session loop

```
Task(Intent Analyst)
→ Task(Planner) creates epic + children via Plane MCP
→ workflow discover
→ Task(Architect)
→ for child in children:
      workflow start --card child  # NOT epic
      Task(Implementer)  # commits autonomously
      Task(QA)           # ruff/pytest/build
      loop AutoFixer max 2 if QA fail
      Task(Reviewer)
      Task(DevOps) push + PR
      workflow finish
→ epic Done when all children Done
```

## After every Task

1. Read `.sdlc/memory/orchestrator-handoff.md`
2. If `stage_complete: false` → Task(same agent) or AutoFixer
3. If `next_agent: qa` → Task(QA) — **do not run pytest yourself**
4. Never merge without Task(Reviewer) APPROVE

## Task prompt template

```
Read .cursor/subagents/<agent>.md and relevant skills.
Card INVES-N (child card, not epic).
Branch: feature/INVES-N-<slug>
Return handoff YAML to .sdlc/memory/orchestrator-handoff.md
Do not ask human to commit, push, or merge.
```

## References

- `.cursor/skills/subagent-delegation/SKILL.md`
- `.cursor/skills/plane-task-creation/SKILL.md`
- `.cursor/skills/qa-minimum-checklist/SKILL.md`
- `.sdlc/scripts/plane_state.py`
- `.sdlc/scripts/auto_merge_pr.py`
