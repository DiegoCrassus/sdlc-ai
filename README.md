# RPG-OP — fichas digitais com SDLC AI-native

RPG-OP é um MVP para criar sandboxes de RPG, subir um modelo de ficha, convidar jogadores e visualizar a ficha no **Sheet Canvas**. A engenharia do projeto segue um SDLC AI-native: contratos em `specs/`, compilador em `packages/rpg_dsl`, artefatos derivados em `generated/`, harness de desenvolvimento em `.sdlc/` e adaptação para Cursor em `.cursor/`.

## Contexto Arquitetural

A fonte colaborativa de arquitetura fica no Plane em `Infrastructure - Project Architecture`. O espelho versionado no repositório é [`docs/infrastructure/project-architecture.md`](docs/infrastructure/project-architecture.md), sincronizado por `make plane-sync-infrastructure`.

A decisão arquitetural atual é manter um monorepo Python + TypeScript:

- Python para backend, DSL, automações, agentes, scripts de SDLC e testes.
- TypeScript para frontend React + Vite.
- `uv` como direção para ambientes Python; hoje o backend operacional ainda usa `backend/requirements.txt`.
- `npm` para o app Vite enquanto não houver outra decisão.
- Plane para documentação colaborativa e `docs/infrastructure/` como espelho versionado.

## Estrutura Atual

```text
rpg-op/
├── .cursor/                  # Regras, skills, agents, MCP e hooks do Cursor
├── .sdlc/                    # Harness SDLC canônico: agents, skills, commands, workflows
├── backend/                  # FastAPI operacional atual
├── apps/
│   ├── web/                  # React + Vite operacional atual
│   ├── backend/              # Placeholder da arquitetura alvo
│   └── frontend/             # Placeholder da arquitetura alvo
├── docs/                     # Arquitetura, produto, status e espelhos Plane
│   ├── infrastructure/
│   └── status/
├── infra/                    # Infraestrutura planejada; migrations ainda como placeholder
├── packages/
│   └── rpg_dsl/              # DSL Python e CLI `rpg`
├── specs/                    # Fonte declarativa de contratos e agentes
├── generated/                # Saída de `rpg compile --target all`; não editar manualmente
├── tests/                    # Estrutura planejada de testes
├── Makefile                  # Entrada operacional local
└── pyproject.toml            # Configuração Ruff da raiz
```

### Transição Importante

Os caminhos operacionais ainda são `backend/` e `apps/web/`. A arquitetura alvo documentada no Plane e em `docs/infrastructure/project-architecture.md` é `apps/backend/` e `apps/frontend/`. A migração física deve acontecer em tarefa própria, porque exige atualizar CI, Makefile, hooks, regras Cursor, docs, imports e scripts SDLC no mesmo PR.

## Componentes

### Backend Atual

`backend/` contém o FastAPI atual:

- `backend/app/main.py` — aplicação e rotas base.
- `backend/app/routers/` — rotas de campanha/workspace.
- `backend/app/models.py` e `backend/app/schemas.py` — modelos SQLAlchemy e Pydantic.
- `backend/data/` — SQLite local e uploads de desenvolvimento.
- `backend/scripts/smoke_test.py` — smoke test operacional.
- `backend/requirements.txt` — dependências de transição.

### Frontend Atual

`apps/web/` contém o app React + Vite:

- React 19, React Router 7, TypeScript e Vite 6.
- `apps/web/src/api.ts` — cliente da API.
- `apps/web/src/pages/` — fluxos de home, criação de campanha e workspace.
- `SheetCanvas` — renderização provisória da ficha com `canvas_spec`, dados mockados e imagem do template.

### DSL, Specs e Generated

`packages/rpg_dsl/` fornece a CLI `rpg` e o compilador de specs. `specs/` declara contratos de ficha, canvas, API BFF e agentes. `generated/` contém OpenAPI, JSON Schema, tipos TypeScript, Pydantic, manifestos de agente e skills geradas.

Regra: nunca edite `generated/` manualmente. Mude `specs/` e rode `rpg compile --target all`.

### SDLC e Integrações

`.sdlc/` é a fonte canônica operacional do agente de engenharia: fases, workflows, commands, skills, subagentes, scripts e integrações. `.cursor/` contém apenas a adaptação para IDE: rules, shortcuts de skills, agents, hooks e MCP.

Integrações principais:

- GitHub para issues, PRs, checks e lifecycle de código.
- Plane para backlog, sprints e documentação.
- LangSmith para observabilidade de hooks e traces do agente.
- Supabase em modo read-only quando configurado.

## Execução Local

Pré-requisitos:

- Python 3.12+
- Node.js 20+
- `uv`
- `make`
- `npm`

Setup completo:

```powershell
make setup
```

Backend:

```powershell
make dev-backend
```

API: http://127.0.0.1:8000  
Swagger: http://127.0.0.1:8000/docs

Frontend:

```powershell
make dev-frontend
```

UI: http://localhost:5173  
Proxy: `/v1` -> http://127.0.0.1:8000

## Validação

```powershell
make lint
make test
make smoke
make validate
```

Notas de estado:

- `make test` roda `pytest` sobre `tests/` e `backend/`.
- A estrutura detalhada de `tests/backend`, `tests/frontend`, `tests/integration` e `tests/e2e` ainda é alvo, não cobertura completa implementada.
- O MVP F1 está sem agente LLM de produto; o próximo passo funcional é o subagente `sheet-template-analyst` da F2.

## Plane, GitHub e Cursor

Para carregar variáveis de ambiente no Cursor e habilitar MCPs:

```powershell
.\launch.ps1
```

Plane:

```powershell
.\.sdlc\scripts\plane-mcp-check.ps1
make plane-sync-infrastructure
```

GitHub:

```powershell
.\.sdlc\scripts\gh-labels-bootstrap.ps1
.\.sdlc\scripts\gh-issue-intent.ps1 -Title "[Intent] Minha feature"
.\.sdlc\scripts\gh-sdlc-status.ps1
```

Hooks + LangSmith:

```powershell
pip install -r .sdlc/requirements-hooks.txt
echo '{}' | python .cursor/hooks/session_start.py
```

Documentação de setup:

- [GitHub MCP](.sdlc/integrations/github.md)
- [Plane MCP](.sdlc/integrations/plane.md)
- [LangSmith](.sdlc/integrations/langsmith.md)
- [Hooks Cursor](.cursor/hooks/README.md)

## Documentação Principal

- [Visão e escopo](docs/01-visao-e-escopo.md)
- [Arquitetura do sistema](docs/02-arquitetura.md)
- [Deep Agent harness](docs/03-deep-agent-harness.md)
- [Infraestrutura](docs/04-infraestrutura.md)
- [Roadmap](docs/05-roadmap.md)
- [SDLC AI-native](docs/06-sdlc-ai-native.md)
- [System Registry](docs/07-system-registry.md)
- [Sheet Canvas](docs/08-sheet-canvas.md)
- [Project Architecture](docs/infrastructure/project-architecture.md)
