---
name: pr-approval-watch
description: Tracks approved PRs into develop, monitors GitHub Actions after approval, and records Plane/GitHub evidence. Use after PR approval or when checks must be watched until stable.
---

# PR Approval Watch

## Workflow

1. Confirm the PR is approved or explicitly ready for develop.
2. Ensure base branch is `develop` for active development work.
3. Watch required Actions until success or failure.
4. If checks fail, create or link a GitHub issue and hand off to `issue-resolver`.
5. If checks pass, run `issue_resolution_validation` for any linked issue that was fixed in the PR.
6. If validation passes and the PR targets `develop`, approve/merge autonomously.
7. If merge is not performed, comment the exact reason on the PR and linked issue.

## Evidence

Record:
- PR URL and number.
- Head SHA.
- Required check names and conclusions.
- Plane cards moved to Done.
- Any issue generated and resolver status.

## Guardrails

- Do not bypass branch protection.
- Do not merge into protected `main` or `staging` directly.
- Stop only after green checks plus merge into `develop`, or explicit blocker evidence explaining why merge was not performed.
