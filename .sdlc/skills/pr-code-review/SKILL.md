---
name: pr-code-review
description: Reviews RPG-OP pull requests for correctness, SDLC compliance, generated artefact policy, tests, security, and Plane/GitHub traceability. Use when a PR is created or updated.
---

# PR Code Review

## Review Order

1. Confirm PR target branch is `develop`, the branch follows `feature/RPG-N` or `bugfix/RPG-N`, and the Plane card is linked.
2. Review diffs for behavioral bugs, secrets, broken workflow policy, and missing tests.
3. Verify local or remote checks are listed as evidence.
4. Leave findings ordered by severity.
5. If a blocking issue exists, create/link the issue and hand off to `issue-resolver`.
6. After the issue is fixed, return to the PR, re-review the latest head SHA, and approve progression to human owner review when no blockers remain.
7. If autonomous merge is not performed, comment the exact reason on the PR.

## Findings Format

- `blocking`: correctness, security, data loss, broken CI, missing Plane traceability, invalid branch naming, or missing required tests.
- `non-blocking`: maintainability, clarity, follow-up work.
- `evidence`: commands, Actions URLs, commit SHA, Plane card IDs.

## Guardrails

- Never approve direct pushes to `main`, `master`, `staging`, or `develop`.
- Do not merge on behalf of a human.
- This repository workflow requires human owner approval before merge into `develop`; if not merged, leave a PR comment explaining why.
