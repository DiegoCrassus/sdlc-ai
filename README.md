# RPG-OP — Fichas digitais com Deep Agents

MVP inicial: criar **sandboxes RPG**, enviar modelo de ficha (imagem), convidar membros e visualizar **ficha exemplo mockada** no canvas.

**SDLC AI-native:** engenharia via Deep Agent — harness em [`.sdlc/`](.sdlc/), IDE em [`.cursor/`](.cursor/).

## Estrutura

```
rpg-op/
├── .cursor/          # Regras e skills Cursor
├── .sdlc/            # Harness dev (agents, skills, commands, workflows)
├── apps/             # Alvo: backend Python + frontend React/Vite
├── docs/             # Arquitetura, status e espelhos Plane
├── infra/            # Migrations e infraestrutura
├── packages/         # Pacotes Python internos
├── specs/            # DSL Python (fonte de contratos)
├── tests/            # Testes backend/frontend/integração/e2e
└── Makefile          # Entrada local padrão
```

Arquitetura alvo: [docs/infrastructure/project-architecture.md](docs/infrastructure/project-architecture.md). Durante a transição, o backend atual ainda está em `backend/` e o frontend atual ainda está em `apps/web/`.

## Pré-requisitos

- Python 3.12+
- Node.js 20+
- uv
- make

## Backend

```powershell
make setup
make dev-backend
```

API: http://127.0.0.1:8000 — docs em http://127.0.0.1:8000/docs

## Frontend

```powershell
make dev-frontend
```

UI: http://localhost:5173 (proxy `/v1` → backend)

## Fluxo

1. **Criar sandbox RPG** — nome, descrição, versão, nº de membros, upload PNG/JPG do modelo de ficha.
2. **Workspace** — convidar e-mails (jogador/mestre), ver ficha exemplo com valores mockados ao lado do modelo enviado.

## Documentação

Ver [docs/](docs/) — [docs/infrastructure/project-architecture.md](docs/infrastructure/project-architecture.md), [06-sdlc-ai-native.md](docs/06-sdlc-ai-native.md), [08-sheet-canvas.md](docs/08-sheet-canvas.md).

## SDLC local + GitHub

```powershell
# Gates locais
.sdlc/scripts/validate.ps1

# GitHub (após gh auth login)
.sdlc/scripts/gh-labels-bootstrap.ps1
.sdlc/scripts/gh-issue-intent.ps1 -Title "[Intent] Minha feature"
.sdlc/scripts/gh-sdlc-status.ps1
```

### GitHub MCP (Cursor)

1. Copie `.env.example` → `.env` e defina `GITHUB_PERSONAL_ACCESS_TOKEN`
2. Exporte a variável no **sistema** (Cursor GUI precisa enxergá-la)
3. Confirme `.cursor/mcp.json` — reinicie Cursor
4. Teste: "Liste issues deste repo via GitHub MCP"

Docs: [.sdlc/integrations/github.md](.sdlc/integrations/github.md)

### Plane MCP (Cursor) — tarefas e docs

1. Conta em https://app.plane.so — gere API token e anote o **workspace slug**
2. `.env`: `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`
3. `.cursor/mcp.json` já inclui server `plane` — abra via `.\launch.ps1`
4. Verifique: `.\.sdlc\scripts\plane-mcp-check.ps1`
5. Teste: "Liste meus projetos no Plane via MCP"

Docs: [.sdlc/integrations/plane.md](.sdlc/integrations/plane.md)

### Hooks + LangSmith

1. `pip install -r .sdlc/requirements-hooks.txt`
2. Defina `LANGCHAIN_API_KEY` e `LANGCHAIN_PROJECT=rpg-op-cursor` no `.env`
3. Reinicie Cursor — Settings → **Hooks** (pre/post listados)
4. Teste: `echo '{}' | python .cursor/hooks/session_start.py`
5. Traces: https://smith.langchain.com/ → projeto `rpg-op-cursor`

Docs: [.cursor/hooks/README.md](.cursor/hooks/README.md) · [.sdlc/integrations/langsmith.md](.sdlc/integrations/langsmith.md)

## Status

F1 implementado (sem agente LLM). Próximo: subagente `sheet-template-analyst` (F2).
