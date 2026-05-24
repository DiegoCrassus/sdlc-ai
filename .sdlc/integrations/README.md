# Integrações — SDLC lifecycle

Plataformas conectadas ao harness Deep Agent via **MCP**, **CLI** e **CI**.

| Plataforma | MCP | CLI | CI | Status |
|------------|-----|-----|-----|--------|
| [GitHub](github.md) | `.cursor/mcp.json` | `gh` | `.github/workflows/` | **ativo** |
| [LangSmith](langsmith.md) | — | hooks Python | eval gate | **ativo** (Cursor) |
| Linear | futuro | — | — | backlog |

Configuração central: [platforms.yaml](platforms.yaml)

## Setup rápido GitHub

1. PAT em https://github.com/settings/tokens — scopes: `repo`, `read:org`, `workflow`
2. Defina `GITHUB_PERSONAL_ACCESS_TOKEN` (system env ou `.env`)
3. Copie `.cursor/mcp.json.example` → `.cursor/mcp.json` se necessário
4. Reinicie o Cursor; verifique MCP verde em Settings → MCP
5. `gh auth login` para comandos locais

## Setup rápido LangSmith

1. API key em https://smith.langchain.com/ → Settings → API Keys
2. `pip install -r .sdlc/requirements-hooks.txt`
3. `.env`: `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT=rpg-op-cursor`
4. Reinicie Cursor; verifique Settings → Hooks
5. Logs locais: `.sdlc/logs/cursor-hooks.jsonl`

## Lifecycle map

Ver [../workflows/github-lifecycle.md](../workflows/github-lifecycle.md)
