# Skill: QA Minimum Checklist

> **Authority:** `docs/sdlc/master-workflow.md` · subagent `qa.md`

## Purpose

QA subagent decides scope but **must** run this minimum checklist before APPROVE handoff.

## When to use

- Every `Task(QA)` after Implementer handoff
- AutoFixer re-runs full checklist after fixes

## Checklist (all required)

| # | Check | Command / evidence |
|---|-------|-------------------|
| 1 | SDLC Doctor | `make sdlc-doctor` exit 0 |
| 2 | Gate tests | `pytest .sdlc/dsl/test_gate.py -q` if SDLC touched |
| 3 | Product tests | `pytest app/` if backend changed |
| 4 | Lint Python | `ruff check app/ .sdlc/` on changed paths |
| 5 | Frontend build | `npm run build` in `app/frontend/` if frontend changed |
| 6 | Plan validation | `validate-all --card INVES-N` if Plane desc changed |
| 7 | AC mapping | Each AC from child card verified individually |

## Handoff YAML

```yaml
agent: qa
card: INVES-N
tests_passed: true|false
doctor_exit: 0
pytest_summary: "N passed"
ruff_summary: "clean|N fixes needed"
build_summary: "ok|skipped|fail"
acceptance_criteria:
  - id: AC-1
    passed: true
next_agent: reviewer  # or auto-fixer if fail
```

## On failure

1. Post `qa_fail` comment on Plane card with output
2. Set `next_agent: auto-fixer`
3. Orchestrator spawns Task(AutoFixer) — **not** inline fixes
4. Max 2 QA→AutoFixer cycles → `human_required`

## Prohibitions

- Never fake test output
- Never skip doctor for "small" changes
- Orchestrator never runs pytest/ruff directly
