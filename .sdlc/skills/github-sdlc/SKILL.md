---
name: github-sdlc
description: >-
  Operates RPG-OP SDLC through GitHub MCP and gh CLI — issues, branches, PRs,
  Actions checks, labels. Use when creating issues, opening PRs, reviewing CI,
  or linking work to the SDLC phases in .sdlc/phases.yaml.
---

# GitHub SDLC

## Prerequisites

- GitHub MCP enabled (`.cursor/mcp.json`, token in `GITHUB_PERSONAL_ACCESS_TOKEN`)
- Optional: `gh auth login` for local scripts

## SDLC ↔ GitHub mapping

| Phase | GitHub artifact | Label |
|-------|-----------------|-------|
| intent | Issue | `sdlc:intent` |
| spec | Issue + branch | `sdlc:spec` |
| implement | Commits on branch | `sdlc:implement` |
| review | Pull Request | — |
| done | Merged PR | close issue |

## MCP workflow (agent)

1. **Read** open issues with label `sdlc:intent` or assigned to current work
2. **Create branch** — `.sdlc/scripts/gh-branch-start.sh feature RPG-123` (skill [branch-naming](../skills/branch-naming/SKILL.md))
3. After spec/implement, **open PR** linking `Closes #N`
4. **Check** Actions / PR checks before asking human to merge
5. **Comment** on issue with summary when phase completes

## PR body template

```markdown
## Summary
- …

## SDLC
- [ ] Spec updated in specs/ (if applicable)
- [ ] validate.sh / make validate green
- [ ] No manual edits to generated/

## Issue
Closes #NN
```

## Do not

- Commit tokens or `.env`
- Force-push `main`
- Merge with failing required checks

## Scripts

- `.sdlc/scripts/gh-branch-start.sh`
- `.sdlc/scripts/gh-issue-intent.sh`
- `.sdlc/scripts/gh-pr-open.sh`
- `.sdlc/scripts/validate.sh`

## Workflows

- [.sdlc/workflows/change-lifecycle.md](../../workflows/change-lifecycle.md)
- [.sdlc/workflows/github-lifecycle.md](../../workflows/github-lifecycle.md)
