# RPG-OP — Cursor agent memory

Memória completa: **[.sdlc/AGENTS.md](../.sdlc/AGENTS.md)**

## GitHub MCP

- Config: **[mcp.json](mcp.json)** — server `github`
- Setup: **[.sdlc/integrations/github.md](../.sdlc/integrations/github.md)**
- Lifecycle: **[.sdlc/workflows/github-lifecycle.md](../.sdlc/workflows/github-lifecycle.md)**

## Quick reference

- SDLC phases: `.sdlc/phases.yaml`
- Dev orchestrator: `.sdlc/agents/dev-orchestrator.yaml`
- Commands: `.sdlc/commands/commands.yaml`
- Skill: `.cursor/skills/sdlc-orchestrator/` + `.sdlc/skills/github-sdlc/`

Ao implementar: **issue → spec → validate → PR → checks → merge**
