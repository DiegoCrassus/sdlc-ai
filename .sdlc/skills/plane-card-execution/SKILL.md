---
name: plane-card-execution
description: Moves Plane work items through execution states and records evidence. Use when starting, completing, reviewing, or linking implementation work to Plane cards.
---

# Plane Card Execution

## Rule

Every executed Plane work item must move state and receive evidence before the agent starts the next independent task.

## State Mapping

- Backlog/Todo: task is planned but not started.
- In Progress: implementation or validation is actively happening.
- Done: acceptance criteria are met, evidence is attached, and any GitHub PR/check link is recorded.
- Cancelled: task is superseded or intentionally skipped; comment why.

## Execution Workflow

1. Resolve the Plane card by identifier.
2. Move it to `In Progress` before making code, docs, GitHub, or infrastructure changes.
3. Execute the task.
4. Add an evidence comment with:
   - GitHub issue/PR links.
   - Commit SHA or branch.
   - Validation commands and outcomes.
   - Remaining risk or follow-up.
5. Move it to `Done` only when acceptance criteria are met.

## Evidence Template

```html
<p><strong>Status:</strong> completed</p>
<p><strong>Evidence:</strong></p>
<ul>
  <li>PR: ...</li>
  <li>Commit: ...</li>
  <li>Checks: ...</li>
</ul>
<p><strong>Residual risk:</strong> ...</p>
```
