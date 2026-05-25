# RPG-OP — fichas digitais com SDLC AI-native

RPG-OP é uma plataforma agnóstica de RPG: cada **workspace** é uma mesa com ficha customizada, provisionamento automático de schema/canvas e visualização no **Sheet Canvas**.

**Toolchain:** 100% shell (`.sh`) — Linux, Ubuntu, WSL ou macOS. Use **bash**; não há scripts PowerShell.

## Contexto Arquitetural

Fonte colaborativa: Plane `Infrastructure - Project Architecture`. Espelho: [`docs/infrastructure/project-architecture.md`](docs/infrastructure/project-architecture.md) — sync via `make plane-sync-infrastructure`.

Monorepo Python + TypeScript:

- Python — backend, DSL, agentes, scripts SDLC, testes
- TypeScript — React + Vite
- `uv` — ambientes Python (`apps/backend/.venv`)
- `npm` — frontend
- Plane — backlog e wiki

## Estrutura

```text
rpg-op/
├── .cursor/           # Rules, skills, MCP, hooks
├── .sdlc/             # Harness SDLC (scripts .sh)
├── apps/
│   ├── backend/       # FastAPI — workspaces, template, sheets
│   └── frontend/      # React + Vite — SheetCanvas, dashboard
├── docs/              # Produto, PoC, status, roadmap
├── packages/rpg_dsl/  # CLI rpg + compilador
├── specs/             # Contratos declarativos
├── generated/         # Saída de rpg compile — não editar
├── tests/             # pytest (18 testes)
├── dev.sh             # Atalho: setup + dev
├── launch.sh          # Cursor com .env
└── Makefile           # Delega para .sdlc/scripts/*.sh
```

Legado `backend/` e `apps/web/` — apenas READMEs de redirecionamento.

## Execução local

Pré-requisitos: **bash**, Python 3.12+, Node 20+, `uv`, `make`, `npm`.

Recomendado: clone em filesystem Linux (`~/projects/`), especialmente no **WSL**.

```bash
bash .sdlc/scripts/bootstrap-linux.sh   # opcional — Ubuntu/WSL
chmod +x dev.sh launch.sh .sdlc/scripts/*.sh
make setup
./dev.sh
```

- App: http://127.0.0.1:5173  
- API: http://127.0.0.1:8000/health  
- Swagger: http://127.0.0.1:8000/docs  

### Comandos make

```bash
make dev              # backend + frontend
make dev-backend      # :8000
make dev-frontend     # :5173
make test             # pytest
make validate         # rpg validate + smoke
make smoke            # requer backend rodando
```

### Cursor + MCP

```bash
./launch.sh
```

### Plane / GitHub

```bash
.sdlc/scripts/plane-mcp-check.sh
.sdlc/scripts/plane-sync-wiki-doc.sh docs/05-roadmap.md
.sdlc/scripts/plane-sync-wiki-doc.sh docs/poc/00-indice-poc.md "PoC - Proof of Concept"
.sdlc/scripts/gh-labels-bootstrap.sh
.sdlc/scripts/gh-sdlc-status.sh
.sdlc/scripts/gh-issue-intent.sh "[Intent] Minha feature"
```

## Validação SDLC

```bash
make lint
make test
make validate
```

## Documentação

- [Índice docs](docs/README.md) · [Roadmap](docs/05-roadmap.md) · [PoC](docs/poc/00-indice-poc.md)
- [SDLC AI-native](docs/sdlc/ai-native.md) · [Sheet Canvas](docs/product/sheet-canvas.md)
- [Status SDLC](docs/status/pendencias-sdlc.md) · [Pendências humanas](docs/status/pendencias-humanas.md)
- [GitHub MCP](.sdlc/integrations/github.md) · [Plane MCP](.sdlc/integrations/plane.md) · [LangSmith](.sdlc/integrations/langsmith.md)
