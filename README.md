# RPG-OP — Fichas digitais com Deep Agents

MVP inicial: criar **sandboxes RPG**, enviar modelo de ficha (imagem), convidar membros e visualizar **ficha exemplo mockada** no canvas.

**SDLC AI-native:** engenharia via Deep Agent — harness em [`.sdlc/`](.sdlc/), IDE em [`.cursor/`](.cursor/).

## Estrutura

```
rpg-op/
├── .sdlc/            # Harness dev (agents, skills, workflows, phases)
├── .cursor/          # Regras e skills Cursor
├── specs/            # DSL Python (fonte da verdade)
├── backend/          # FastAPI (API /v1)
├── apps/web/         # React + Vite (UI provisória)
└── docs/             # Arquitetura e roadmap
```

## Pré-requisitos

- Python 3.12+
- Node.js 20+

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API: http://127.0.0.1:8000 — docs em http://127.0.0.1:8000/docs

## Frontend

```powershell
cd apps/web
npm install
npm run dev
```

UI: http://localhost:5173 (proxy `/v1` → backend)

## Fluxo

1. **Criar sandbox RPG** — nome, descrição, versão, nº de membros, upload PNG/JPG do modelo de ficha.
2. **Workspace** — convidar e-mails (jogador/mestre), ver ficha exemplo com valores mockados ao lado do modelo enviado.

## Documentação

Ver [docs/](docs/) — [06-sdlc-ai-native.md](docs/06-sdlc-ai-native.md), [08-sheet-canvas.md](docs/08-sheet-canvas.md).

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

### Hooks + LangSmith

1. `pip install -r .sdlc/requirements-hooks.txt`
2. Defina `LANGCHAIN_API_KEY` e `LANGCHAIN_PROJECT=rpg-op-cursor` no `.env`
3. Reinicie Cursor — Settings → **Hooks** (pre/post listados)
4. Teste: `echo '{}' | python .cursor/hooks/session_start.py`
5. Traces: https://smith.langchain.com/ → projeto `rpg-op-cursor`

Docs: [.cursor/hooks/README.md](.cursor/hooks/README.md) · [.sdlc/integrations/langsmith.md](.sdlc/integrations/langsmith.md)

## Status

F1 implementado (sem agente LLM). Próximo: subagente `sheet-template-analyst` (F2).
