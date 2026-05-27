# Command: SDLC Implement

## Purpose

Implement a planned task with proper context loading, focused diff, validation, and docs update if needed.

## When to Use

- When a plan or architecture has been approved
- When entering the Implementation stage
- When applying an auto-fix from an incident

## Procedure

### Step 1 — Load Implementation Context

1. Read `.sdlc/stages.yaml` for implementation stage gates.
2. Read the Plane work item (MCP) for this task — description, acceptance criteria, DoD.
3. Read `.sdlc/memory/architecture.md` to confirm boundaries.
4. Identify the exact files that will change.

### Step 2 — Pre-Implementation Checklist

Before writing code, confirm:
- [ ] Architecture is documented and approved
- [ ] Acceptance criteria are clear
- [ ] Tests will be added for new logic
- [ ] Docs will be updated if interfaces or architecture change

### Step 3 — Implement

Rules:
- Make the smallest change that satisfies the acceptance criteria.
- Do not touch files outside the task scope.
- Do not mix refactoring with feature work.
- Do not reformat unrelated code.
- Add type hints to all new Python functions.
- Write tests alongside the implementation, not after.

### Step 4 — Self-Review

After implementing, check:
- [ ] All new logic has tests
- [ ] No unrelated files changed
- [ ] No commented-out code left in
- [ ] No `print` statements in library code
- [ ] Docs updated if needed (public interface, architecture, infra)

### Step 5 — Validation

Run:
```bash
# Run tests (add the correct command when tests exist)
python -m pytest app/ -v

# Run Doctor if structure changed
make sdlc-doctor
```

Report actual results. Do not fake passing.

### Step 6 — Output

Provide:
1. Summary of changes made
2. Files changed (list)
3. Test results (actual output)
4. Docs updated (list or "none needed")
5. Next step (Validation or PR & Review)

## Failure Modes

- Tests fail → fix the implementation, not the test assertions
- Doctor fails → fix the structural issue, not the Doctor rules
- Scope creep detected → stop, reduce scope, document the remainder
