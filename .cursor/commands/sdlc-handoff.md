# Command: SDLC Handoff

## Purpose

Generate a handoff summary for a completed stage or work unit. Captures what changed, why, risks, validation evidence, next steps, and rollback notes.

## When to Use

- Before a major stage transition (requirements → architecture, architecture → implementation, etc.)
- When finishing a sprint or work batch
- When handing off to another agent or developer
- To update `docs/handoff/current-state.md`

## Procedure

### Step 1 — Collect Context

1. Read the current `docs/handoff/current-state.md`.
2. Read recent changes (files modified, docs updated).
3. Read the original plan or ticket.
4. Identify the SDLC stage that is completing.

### Step 2 — Produce the Handoff Document

```markdown
## Handoff: <title>

- **Date:** YYYY-MM-DD
- **Stage Completed:** <stage id>
- **Next Stage:** <stage id>
- **Author:** <agent or human>

### What Changed
- <file or component>: <what was done>

### Why It Changed
<business or technical reason>

### Validation Evidence
- [ ] Tests passed: <test output summary or "not applicable">
- [ ] Doctor passed: <yes | no — include output summary>
- [ ] Acceptance criteria met: <list each criterion and status>

### Known Risks
| Risk | Severity | Mitigation |
|------|----------|------------|

### Open Questions
- <question 1>

### Next Steps
1. <next action>
2. <next action>

### Rollback
<How to revert if needed. "N/A" only if the change is truly irreversible and documented.>
```

### Step 3 — Update Current State

Append or update `docs/handoff/current-state.md` with the new handoff summary.

### Step 4 — Verify

- [ ] All sections are filled in (not left blank)
- [ ] Validation evidence is real (not claimed)
- [ ] Next steps are actionable

## Failure Modes

- No validation evidence → do not write "passed" — document what was and was not verified
- Rollback unclear → document explicitly as "unknown — requires manual assessment"
- Open questions → record them, do not suppress
