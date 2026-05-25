# Plane — MCP para tarefas e documentação

Integração oficial: [makeplane/plane-mcp-server](https://github.com/makeplane/plane-mcp-server) · Docs: [developers.plane.so](https://developers.plane.so/dev-tools/mcp-server)

O Plane MCP expõe **100+ tools** para work items (tarefas), cycles (sprints), modules, labels, comments e **Pages** (wiki/documentação).

## Papel no SDLC RPG-OP

| Ferramenta | Foco |
|------------|------|
| **GitHub** | Código, issues técnicas, PRs, CI |
| **Plane** | Backlog de produto, sprints, documentação wiki |

Use Plane para planejar e documentar; GitHub para implementar e revisar código.

## Pré-requisitos

1. Conta no [Plane Cloud](https://app.plane.so) **ou** instância self-hosted
2. Acesso a pelo menos um workspace
3. Cursor **v0.48+** (suporte a `${env:...}` no `mcp.json`)

## Credenciais

### API key (PAT ou workspace token)

1. Abra o Plane → seu workspace
2. Gere um token:
   - **Personal Access Token** — Profile Settings → API Tokens
   - **Workspace Access Token** — Workspace Settings → Access Tokens
3. Clique **Add access token**, nomeie (ex.: `cursor-mcp`), **Generate token**
4. Copie o token — ele não será exibido novamente

### Workspace slug

O slug é o identificador curto na URL do Plane:

```
https://app.plane.so/acme-corp/
                      ^^^^^^^^^
                      slug = acme-corp
```

### Variáveis de ambiente

Adicione ao `.env` na raiz (copie de `.env.example`):

```env
PLANE_API_KEY=
PLANE_WORKSPACE_SLUG=
# Opcional — só para self-hosted (default: https://api.plane.so)
# PLANE_BASE_URL=https://plane.suaempresa.com
```

> Nunca commite `.env` ou tokens no `mcp.json`.

## MCP no Cursor (projeto)

Arquivo: [`.cursor/mcp.json`](../../.cursor/mcp.json)

Copie de [`.cursor/mcp.json.example`](../../.cursor/mcp.json.example) se ainda não existir.

### HTTP com API key (recomendado)

Melhor para agentes e automação — sem fluxo OAuth no browser.

```json
{
  "mcpServers": {
    "github": { "...": "..." },
    "plane": {
      "url": "https://mcp.plane.so/http/api-key/mcp",
      "headers": {
        "x-api-key": "${env:PLANE_API_KEY}",
        "x-workspace-slug": "${env:PLANE_WORKSPACE_SLUG}"
      }
    }
  }
}
```

### HTTP com OAuth (alternativa)

Setup mais simples para uso individual — o Cursor abre o browser na primeira conexão.

```json
{
  "mcpServers": {
    "plane": {
      "url": "https://mcp.plane.so/http/mcp"
    }
  }
}
```

Não requer `PLANE_API_KEY` no `.env`.

### Stdio local (self-hosted)

Para Plane self-hosted ou quando preferir processo local via `uvx`:

Requisitos: Python 3.10+, [uv](https://docs.astral.sh/uv/getting-started/installation/)

```json
{
  "mcpServers": {
    "plane": {
      "command": "uvx",
      "args": ["plane-mcp-server", "stdio"],
      "env": {
        "PLANE_API_KEY": "${env:PLANE_API_KEY}",
        "PLANE_WORKSPACE_SLUG": "${env:PLANE_WORKSPACE_SLUG}",
        "PLANE_BASE_URL": "${env:PLANE_BASE_URL}"
      }
    }
  }
}
```

Para self-hosted, `PLANE_BASE_URL` deve apontar para a URL pública da sua instância (ex.: `https://plane.suaempresa.com`).

## Ativar no Cursor

1. Preencha `PLANE_API_KEY` e `PLANE_WORKSPACE_SLUG` no `.env`
2. Confirme que `.cursor/mcp.json` inclui o server `plane`
3. **Reinicie o Cursor com variáveis carregadas:**

   ```powershell
   .\launch.ps1
   ```

   O script carrega o `.env` e abre o Cursor — necessário para `${env:PLANE_*}` funcionar.

4. Settings → **MCP** → server `plane` deve aparecer **verde**
5. No chat Agent, peça: *"Liste meus projetos no Plane"* — deve chamar `list_projects`

### Verificar credenciais (PowerShell)

```powershell
. .\.sdlc\scripts\_load-env.ps1
.\.sdlc\scripts\plane-mcp-check.ps1
```

Ou manualmente:

```powershell
curl -H "x-api-key: $env:PLANE_API_KEY" "https://api.plane.so/api/v1/users/me/"
```

Resposta `200` confirma API key válida.

## Sincronizar docs do repo para a wiki

**Importante:** a **Wiki** fica no nivel do **workspace** (menu lateral Wiki).
**Pages** dentro de um **projeto** (ex.: RPG → Pages) e outra secao — nao confundir.

```powershell
# Roadmap na Wiki do workspace (recomendado)
.\.sdlc\scripts\plane-sync-wiki-doc.ps1 -DocPath docs/05-roadmap.md

# Alternativa: page vinculada ao projeto RPG
.\.sdlc\scripts\plane-sync-wiki-doc.ps1 -DocPath docs/05-roadmap.md -Scope project
```

Onde encontrar na UI do Plane:

| Onde | Caminho na UI | URL |
|------|---------------|-----|
| **Wiki (workspace)** | Sidebar → **Wiki** | `https://app.plane.so/<slug>/wiki/` |
| **Pages (projeto)** | Projeto RPG → **Pages** | `https://app.plane.so/<slug>/projects/RPG/` → Pages |

Diagnostico:

```powershell
.\.sdlc\scripts\plane-wiki-diagnose.ps1
```

Converte Markdown para HTML (`plane_md_to_html.py`) e cria/atualiza via `POST /api/v1/workspaces/{slug}/pages/`.

## O que o agente pode fazer

### Tarefas (work items)

| Tool | Uso |
|------|-----|
| `list_projects` | Listar projetos do workspace |
| `list_work_items` | Filtrar tarefas por estado, assignee, prioridade |
| `create_work_item` | Criar tarefa |
| `retrieve_work_item_by_identifier` | Buscar por ID legível (ex.: `ENG-42`) |
| `update_work_item` | Atualizar estado, assignee, prioridade |
| `create_work_item_comment` | Comentar em tarefa |
| `search_work_items` | Busca textual |

### Sprints e organização

| Tool | Uso |
|------|-----|
| `list_cycles` / `create_cycle` | Sprints |
| `list_modules` | Módulos/epics |
| `list_states` | Colunas do board |
| `list_labels` | Etiquetas |

### Documentação (Pages)

| Tool | Uso |
|------|-----|
| `create_workspace_page` | Wiki no nível do workspace |
| `create_project_page` | Doc vinculada a um projeto |
| `retrieve_workspace_page` | Ler página do workspace |
| `retrieve_project_page` | Ler página de projeto |

Skill do agente: [.sdlc/skills/plane-sdlc/SKILL.md](../skills/plane-sdlc/SKILL.md)

Workflow SDLC: [.sdlc/workflows/plane-lifecycle.md](../workflows/plane-lifecycle.md)

## Identificadores Plane

- **Legível** — ex.: `ENG-42` (projeto `ENG`, número `42`) — use em conversa
- **UUID** — ex.: `3fa85f64-...` — retornado pela API; necessário para updates

Fluxo típico: `list_projects` → obter `project_id` → `retrieve_work_item_by_identifier` com `project_identifier` + `work_item_identifier`.

## Troubleshooting

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| MCP vermelho / auth failed | Token inválido ou revogado | Regenerar token no Plane |
| 404 workspace | Slug errado | Conferir URL do workspace |
| `${env:PLANE_*}` não resolve | Cursor aberto sem `.env` | Usar `.\launch.ps1` |
| Tools não aparecem | MCP desabilitado | Settings → MCP → enable `plane` |
| Self-hosted falha | URL incorreta | Ajustar `PLANE_BASE_URL` |

Referência completa de tools: [developers.plane.so/dev-tools/mcp-server](https://developers.plane.so/dev-tools/mcp-server)

## Segurança

- Nunca commitar `PLANE_API_KEY` em `mcp.json`, specs ou docs
- `.env` está no `.gitignore`
- Hooks Cursor auditam chamadas MCP (`.cursor/hooks/before_mcp.py`) sem logar secrets
