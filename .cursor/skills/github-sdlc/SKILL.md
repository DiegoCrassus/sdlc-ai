---
name: github-sdlc
description: Work with GitHub pull requests, CI status, issue links, releases, and merge evidence for the SDLC pipeline. Use when DevOps, Reviewer, or Orchestrator needs GitHub context, PR creation, CI checks, or merge status.
disable-model-invocation: true
---

# GitHub SDLC

## Purpose

Standardize GitHub operations in the SDLC pipeline. Plane remains the primary workboard; GitHub is used for PRs, CI evidence, issue triage, and merge records.

## When to use

- Creating or reviewing a PR for an `INVES-N` card.
- Checking CI before `workflow finish`.
- Linking GitHub issues to Plane cards.
- Preparing release or rollback notes tied to a PR.

## Procedure

1. Read `.sdlc/process/change-lifecycle.md`.
2. Confirm the active Plane card and branch from `.sdlc/memory/orchestrator-handoff.md` and `workflow status`.
3. Use the repository default base branch from `.sdlc/sdlc.yaml` (`develop`).
4. Collect real evidence: PR URL, CI status, merge commit, rollback command.
5. Record evidence on Plane through `finish-change` / DevOps flow.

## Boundaries

- Do not use GitHub Issues as the primary tracker; Plane cards are source of truth.
- Do not merge without Reviewer APPROVE and green CI.
- Do not force-push or bypass branch protections.

## Related files

- `.cursor/skills/finish-change/SKILL.md`
- `.sdlc/scripts/auto_merge_pr.py`
- `.sdlc/scripts/github_issue_triage.py`
- `.sdlc/integrations/services.yaml`
