# Integrações — SDLC lifecycle

Plataformas conectadas ao harness Deep Agent via **MCP**, **CLI** e **CI**.

| Plataforma | MCP | CLI | CI | Status |
|------------|-----|-----|-----|--------|
| [GitHub](github.md) | `.cursor/mcp.json` | `gh` | `.github/workflows/` | **ativo** |
| [Plane](plane.md) | `.cursor/mcp.json` | — | — | **ativo** |
| [LangSmith](langsmith.md) | — | hooks Python | eval gate | **ativo** (Cursor) |
| Linear | futuro | — | — | backlog |

Configuração central: [platforms.yaml](platforms.yaml)

## Setup rápido GitHub

1. PAT em https://github.com/settings/tokens — scopes: `repo`, `read:org`, `workflow`
2. Defina `GITHUB_PERSONAL_ACCESS_TOKEN` (system env ou `.env`)
3. Copie `.cursor/mcp.json.example` → `.cursor/mcp.json` se necessário
4. Reinicie o Cursor; verifique MCP verde em Settings → MCP
5. `gh auth login` para comandos locais

## Setup rápido Plane

1. Conta em https://app.plane.so — gere API token (Profile ou Workspace Settings)
2. Anote o **workspace slug** da URL (`https://app.plane.so/<slug>/`)
3. `.env`: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`
4. `.cursor/mcp.json` já inclui server `plane` (ver `mcp.json.example`)
5. `.\launch.ps1` → Settings → MCP → `plane` verde
6. Verifique: `.\.sdlc\scripts\plane-mcp-check.ps1`

Doc completa: [plane.md](plane.md)

## Setup rápido LangSmith

1. API key em https://smith.langchain.com/ → Settings → API Keys
2. `pip install -r .sdlc/requirements-hooks.txt`
3. `.env`: `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT=rpg-op-cursor`
4. Reinicie Cursor; verifique Settings → Hooks
5. Logs locais: `.sdlc/logs/cursor-hooks.jsonl`

## Lifecycle map

Ver [../workflows/github-lifecycle.md](../workflows/github-lifecycle.md)
