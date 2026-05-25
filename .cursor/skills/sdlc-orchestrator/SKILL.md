---
name: sdlc-orchestrator
description: >-
  Run RPG-OP SDLC with .sdlc/ harness and GitHub MCP — issues, PRs, spec, compile,
  validate. Use when planning features or operating the full lifecycle.
---

# SDLC orchestrator (Cursor)

## Start here

1. Read `.cursor/agents/dev-orchestrator.md`
2. Read `.sdlc/agents/dev-orchestrator.yaml`
3. Read `.sdlc/workflows/github-lifecycle.md`
4. Read `.sdlc/AGENTS.md`
5. Enable **GitHub MCP** (`.cursor/mcp.json` + token)

## Agent Boundary

- Cursor adapters live in `.cursor/agents/`.
- Canonical operational YAML lives in `.sdlc/agents/`.
- Do not duplicate skills, tools, permissions, or model config in Cursor adapters.

## GitHub

- MCP for issues, PRs, checks in chat
- Scripts: `.sdlc/scripts/gh-*.ps1`
- Skill: `.sdlc/skills/github-sdlc/SKILL.md`

## Validate locally

```powershell
.sdlc/scripts/validate.ps1
.sdlc/scripts/gh-sdlc-status.ps1
```
