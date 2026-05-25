---
name: issue-resolution-validation
description: Validates that a resolved GitHub issue is truly closed by checks, PR review, Plane evidence, and develop integration. Use after issue-resolver claims a fix is done.
---

# Issue Resolution Validation

## Workflow

1. Confirm the issue is linked to a PR, branch, commit, and Plane card.
2. Confirm the fix commit is present on the PR branch.
3. Verify required Actions are green on the latest PR head.
4. Re-run code review on the changed PR surface.
5. If no blockers remain and base is `develop`, approve and merge autonomously.
6. If autonomous merge is not possible, comment the exact blocker on the PR and issue.
7. Close the issue only after validation passes and evidence is recorded.

## Required Evidence

- Issue number and state.
- PR number, base branch, head SHA, and mergeability.
- Required Actions and conclusions.
- Code-review result after the fix.
- Plane card state and evidence comment.
- Merge result or explicit reason merge was not performed.

## Guardrails

- Do not validate against stale Actions from an older head SHA.
- Do not close an issue while the PR remains blocked.
- Do not merge into `main` or `staging` directly.
