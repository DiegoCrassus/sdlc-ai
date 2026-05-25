---
name: pr-code-review
description: Reviews RPG-OP pull requests for correctness, SDLC compliance, generated artefact policy, tests, security, and Plane/GitHub traceability. Use when a PR is created or updated.
---

# PR Code Review

## Review Order

1. Confirm PR target branch and linked GitHub issue/Plane card.
2. Review diffs for behavioral bugs, schema drift, generated-file policy, secrets, and missing tests.
3. Verify local or remote checks are listed as evidence.
4. Leave findings ordered by severity.
5. If a blocking issue exists, create/link the issue and hand off to `issue-resolver`.
6. After the issue is fixed, return to the PR, re-review the latest head SHA, and approve progression to `develop` when no blockers remain.
7. If autonomous merge is not performed, comment the exact reason on the PR.

## Findings Format

- `blocking`: correctness, security, data loss, broken CI, or missing required spec.
- `non-blocking`: maintainability, clarity, follow-up work.
- `evidence`: commands, Actions URLs, commit SHA, Plane card IDs.

## Guardrails

- Never approve direct pushes to `main` or `staging`.
- Never approve manual edits to `generated/`; require `rpg compile`.
- Do not merge on behalf of a human unless the workflow explicitly allows it.
- This repository workflow allows autonomous merge into `develop` after issue-resolution validation passes; if not merged, leave a PR comment explaining why.
