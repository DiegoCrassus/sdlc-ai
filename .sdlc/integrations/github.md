# GitHub — MCP, gh CLI e CI

Integração oficial: [github/github-mcp-server](https://github.com/github/github-mcp-server)

## MCP no Cursor (projeto)

Arquivo: [`.cursor/mcp.json`](../../.cursor/mcp.json)

### Remote (recomendado)

```json
{
  "mcpServers": {
    "github": {
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${env:GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

Requer Cursor **v0.48+**. Se `${env:...}` falhar, cole o PAT direto no header via Settings → MCP → editar `github`, ou lance o Cursor a partir de um terminal com a variável exportada.

### Local (Docker)

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${env:GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

> Não use `@modelcontextprotocol/server-github` (npm) — deprecado.

## Personal Access Token — scopes

| Scope | Uso |
|-------|-----|
| `repo` | Issues, PRs, branches, contents |
| `read:org` | Teams (opcional) |
| `workflow` | Disparar/rever Actions |

Fine-grained PAT: repositório `rpg-op`, Contents R/W, Issues R/W, Pull requests R/W, Actions R.

## MCP — o que o agente pode fazer

Via GitHub MCP tools (nomes podem variar por versão):

- Listar/criar/atualizar **issues**
- Ler/criar **pull requests**, reviews, comentários
- Consultar **Actions** / checks
- Buscar arquivos e commits no repo
- Gerenciar **branches** (criar a partir de issue)

Use a skill [.sdlc/skills/github-sdlc/SKILL.md](../skills/github-sdlc/SKILL.md).

## gh CLI — comandos do lifecycle

Instalação: https://cli.github.com/

Autenticação:

```powershell
gh auth login
gh auth setup-git
```

Ver [.sdlc/commands/github.md](../commands/github.md) e scripts em `.sdlc/scripts/`.

## Branching (convenção)

```
main          # produção
develop       # integração (opcional)
feat/<issue>-<slug>
fix/<issue>-<slug>
sdlc/<phase>-<slug>
```

## Issue ↔ SDLC

- Label `sdlc:intent` — fase 1
- `sdlc:spec` — spec/DSL
- `sdlc:ready` — pronto para implement
- `sdlc:blocked` — aguardando humano

Templates: `.github/ISSUE_TEMPLATE/`

## PR ↔ gates

CI workflow `SDLC` roda validate + pytest. PR template exige checklist SDLC.

## Segurança

- Nunca commitar PAT em `mcp.json`, `.env`, ou specs
- `.env` está no `.gitignore`
- Secrets no GitHub: Settings → Secrets → Actions (`OPENAI_API_KEY`, etc.)
