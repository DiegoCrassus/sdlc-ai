---
name: plane-task-creation
description: >-
  Standardizes creation of Plane work items with strongly documented scope. Use
  when creating, drafting, reviewing, or updating Plane tasks, backlog items, or
  work item descriptions.
---

# Plane Task Creation

## Non-negotiable rule

Every Plane task must be very well documented before creation. Do not create vague,
placeholder, or minimally scoped tasks. If the scope is incomplete, ask follow-up
questions or inspect the available project context before creating the task.

The task description must make the work clear enough that another engineer or agent
can implement it without relying on hidden chat context.

## Required description model

Use these exact sections, in this order:

```markdown
## context

## changes

## acceptance criteria

## comments
```

## GitHub and branch linkage (required in comments)

Every task that will touch code must record in `comments`:

- **Plane ID:** `RPG-123` (used for branch naming)
- **Branch (planned):** `feature/RPG-123` or `bugfix/RPG-123`
- **GitHub issue:** `#N` or "a criar via gh-issue-intent"
- **SDLC commands:** `start_change` → implement → `finish_change`

When creating the task, also set the work item **title** prefix:

| Type | Title prefix | Branch prefix |
|------|--------------|---------------|
| Feature | `[Feature]` | `feature/RPG-N` |
| Bugfix | `[Bugfix]` | `bugfix/RPG-N` |
| Spec-only | `[Spec]` | `feature/RPG-N` |
| Docs | `[Docs]` | `feature/RPG-N` |

## Section requirements

- `context`: Explain why the task exists, what problem it solves, relevant links or artifacts, current behavior, and any constraints.
- `changes`: Describe the expected implementation scope in concrete terms, including files, systems, workflows, integrations, or documentation likely affected when known.
- `acceptance criteria`: List verifiable outcomes. Each criterion must be testable by a human, CI check, local command, UI behavior, or explicit review condition.
- `comments`: Record assumptions, dependencies, risks, open questions, follow-up notes, Plane/GitHub links, or decisions made while preparing the task.

## Creation workflow

1. Resolve the target Plane project, cycle, module, and priority when applicable.
2. Draft the full task description using the required model.
3. Check whether the task scope is specific, actionable, and independently understandable.
4. Create the Plane work item only after the description passes the documentation check.
5. After creation, report the Plane task identifier and use it for branch naming when work begins.
6. If GitHub issue is missing, propose creating one with `gh-issue-intent.sh` or GitHub MCP.

## Quality bar

A Plane task is not ready if:

- It has empty or generic sections.
- It says only "implement X" without explaining context and expected changes.
- Acceptance criteria are subjective or impossible to verify.
- Important assumptions remain only in the chat instead of the task description.
- The work depends on a missing decision and no comment records that dependency.

## Minimal template

```markdown
## context

Describe the problem, goal, current behavior, constraints, and relevant references.

## changes

Describe the concrete implementation or documentation changes expected.

## acceptance criteria

- [ ] Verifiable outcome 1.
- [ ] Verifiable outcome 2.

## comments

- Plane: RPG-123 → branch `feature/RPG-123`
- GitHub: issue #42 (ou criar)
- SDLC: start_change → finish_change
- Assumptions, risks, dependencies.
```
