---
name: branch-naming
description: >-
  Standardizes branch creation for RPG-OP using Plane task identifiers. Use when
  creating, renaming, checking out, or reviewing git branches for repository work.
---

# Branch Naming

## Required format

Branches in this repository must use one of these prefixes followed by the Plane task identifier:

```text
feature/<plane-task-id>
bugfix/<plane-task-id>
```

Examples:

```text
feature/RPG-123
bugfix/RPG-456
```

## Rules

- Use `feature/` for new functionality, enhancements, specs, or planned implementation work.
- Use `bugfix/` for defect fixes, regressions, failing tests, or production issues.
- The segment after `/` must be the Plane task identifier, not a free-form title.
- Do not use GitHub issue numbers, local slugs, author names, dates, or mixed prefixes in the branch name.
- The Plane work item must exist before GitHub workflow starts. If the Plane task identifier is unknown, create or retrieve the Plane task before creating the branch.
- Branches must start from `develop`. Do not branch from `main`, `master`, `staging`, or another feature branch unless the user explicitly approves an exception.

## Workflow

1. Identify whether the work is a feature or bugfix.
2. Resolve the Plane task identifier, for example `RPG-123`.
3. Sync `develop`, then create or switch to the branch:

```bash
.sdlc/scripts/gh-branch-start.sh feature RPG-123
.sdlc/scripts/gh-branch-start.sh bugfix RPG-456
```

## Validation

Before creating a PR or reporting branch status, verify the current branch matches:

```text
^(feature|bugfix)/[A-Za-z]+-[0-9]+$
```
