# Validation Gates

## What Are Gates?

Gates are conditions that must be true before a stage transition is allowed. They prevent unfinished or unverified work from advancing through the lifecycle.

Gates are defined per stage in `.sdlc/stages.yaml`.

## Gate Enforcement

Gates are enforced by:
1. **Doctor** — checks structural and configuration gates
2. **QA subagent** — checks test and acceptance criteria gates
3. **Reviewer subagent** — checks review and security gates
4. **Rules** (`.sdlc/rules.yaml`) — governance gates

## Gates by Stage

### Ticket Gate

- [ ] Acceptance criteria are explicit and measurable (not "it should work")
- [ ] Scope is bounded (not "refactor everything")

### Requirements Gate

- [ ] Non-goals explicitly documented (at least 2)
- [ ] Risks have mitigations or accepted status (at least 2 risks)
- [ ] Scope statement is written

### Architecture Gate

- [ ] Trade-offs documented (not just the chosen option)
- [ ] Impacted areas listed
- [ ] No code written before this gate passes

### Implementation Gate

- [ ] Tests exist for all new logic
- [ ] Diff is focused (no unrelated changes)
- [ ] Docs updated if public interfaces or architecture changed

### Validation Gate

- [ ] All required tests pass (actual output recorded)
- [ ] No fake validation
- [ ] Each acceptance criterion verified individually

### PR & Review Gate

- [ ] Security considerations checked
- [ ] No unaddressed high-risk items
- [ ] Test coverage verified
- [ ] Doctor passed

### Deployment Gate

- [ ] Rollback plan exists and is documented
- [ ] Environment variables verified
- [ ] Review approved

### Observability Gate

- [ ] At least error logging confirmed at all failure paths
- [ ] Key metrics identified
- [ ] Alert defined for service-down condition

## Hard Gates vs. Soft Gates

**Hard gate** — Must pass before proceeding. Violation is a required FAIL in Doctor or review.

Examples:
- Tests must pass before review
- Doctor must pass before deployment
- Human review required before auto-fix merge

**Soft gate** — Warning if not met. Must be explicitly accepted or addressed.

Examples:
- Test coverage below threshold
- No observability stack configured
- Optional integrations not set up

## Gate Failure Handling

When a gate fails:
1. Report the specific failure.
2. Fix the root cause — do not bypass the gate.
3. Re-run the check.
4. Only proceed when the gate passes.

Never mark a gate as passed without evidence.
