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
5. If checks pass, comment evidence on the PR, linked GitHub issue, and Plane card.

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
- Stop only on green checks or explicit blocker evidence.
