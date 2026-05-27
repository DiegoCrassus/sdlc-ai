# Command: SDLC Plan

## Purpose

Convert an idea or ticket into a structured, SDLC-aligned plan with scope, assumptions, risks, affected areas, tasks, and validation gates.

## When to Use

- When starting work on a new feature, fix, or change
- When a ticket arrives without a structured specification
- Before entering the Requirements or Architecture stage

## Procedure

### Step 1 — Load Context

1. Read `.sdlc/sdlc.yaml` to understand current configuration.
2. Read `.sdlc/memory/architecture.md` for current boundaries.
3. Read `.sdlc/memory/business-rules.md` for domain constraints.
4. Read `docs/architecture/overview.md` for system context.

### Step 2 — Clarify the Ticket

If the input is vague, ask for:
- Business intent (why is this needed?)
- Expected behavior (what should happen?)
- Acceptance criteria (how do we know it's done?)
- Constraints (what must NOT change?)

### Step 3 — Produce the Plan

Output a structured plan with these sections:

```markdown
## Plan: <ticket title>

### Stage
Requirements / Architecture / Implementation (current stage)

### Scope
What will be done.

### Non-Goals
What will NOT be done.

### Assumptions
What we are assuming (with confidence: high | medium | low).

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

### Affected Areas
- Files and directories impacted
- External services affected
- Docs that must be updated

### Tasks
1. [ ] Task description
2. [ ] Task description

### Validation Gates
- How will we know each acceptance criterion is met?
- What tests are needed?

### Next Step
What the Implementer or Architect should do first.
```

### Step 4 — Validate the Plan

- Each acceptance criterion must be measurable.
- At least 2 risks identified.
- Non-goals explicitly stated.
- Scope is bounded.

## Outputs

- Structured plan (as above)
- Plane work item updated via MCP with full plan in description (never a local `specs/` file)

## Failure Modes

- Missing acceptance criteria → ask before producing the plan
- Scope too broad → reduce to a focused increment and document the rest as future work
- Unknown architecture constraints → load memory files, flag assumptions
