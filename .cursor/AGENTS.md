# RPG-OP — Cursor agent memory

Memória completa: **[.sdlc/AGENTS.md](../.sdlc/AGENTS.md)**

## Cursor Agents

- Adapters: **[agents/](agents/)** — instruções de uso no Cursor.
- Fonte canônica: **[.sdlc/agents/](../.sdlc/agents/)** — YAMLs operacionais.
- Regra: não duplicar configuração operacional em `.cursor/agents/`; alterar skills, tools, permissões e prompts em `.sdlc/agents/`.

## GitHub MCP

- Config: **[mcp.json](mcp.json)** — server `github`
- Setup: **[.sdlc/integrations/github.md](../.sdlc/integrations/github.md)**
- Lifecycle: **[.sdlc/workflows/github-lifecycle.md](../.sdlc/workflows/github-lifecycle.md)**

## Plane MCP

- Config: **[mcp.json](mcp.json)** — server `plane`
- Setup: **[.sdlc/integrations/plane.md](../.sdlc/integrations/plane.md)**
- Lifecycle: **[.sdlc/workflows/plane-lifecycle.md](../.sdlc/workflows/plane-lifecycle.md)**

## Supabase MCP

- Config: **[mcp.json](mcp.json)** — server `supabase`
- Setup: **[.sdlc/integrations/supabase.md](../.sdlc/integrations/supabase.md)**
- Mode: `read_only=true` scoped by `SUPABASE_PROJECT_REF`

## Quick reference

- SDLC phases: `.sdlc/phases.yaml`
- Dev orchestrator: `.sdlc/agents/dev-orchestrator.yaml`
- Cursor adapter: `.cursor/agents/dev-orchestrator.md`
- Commands: `.sdlc/commands/commands.yaml` + playbooks em `.sdlc/commands/*.md`
- Skill: `.cursor/skills/sdlc-orchestrator/` + `.sdlc/skills/github-sdlc/` + `.sdlc/skills/plane-sdlc/`

Ao implementar: **issue → spec → validate → PR → checks → merge**
