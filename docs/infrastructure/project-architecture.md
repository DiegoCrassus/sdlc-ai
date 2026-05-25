# Project Architecture

## Fonte de verdade

A fonte colaborativa de verdade para arquitetura de infraestrutura deve existir no Plane em:

```text
Infrastructure / Project Architecture
```

Este arquivo é o espelho versionado no repositório e deve ser sincronizado pelo command `.sdlc/commands/architecture-documentation.md`.

## Decisão arquitetural

O projeto RPG-OP deve ser organizado como um monorepo predominantemente Python + TypeScript:

- Python para backend, DSL, automações, agentes, scripts de SDLC e testes.
- TypeScript para frontend React + Vite.
- `uv` como ferramenta padrão para ambientes e dependências Python.
- `npm` para o app Vite enquanto não houver decisão explícita por outro gerenciador Node.
- Plane `Infrastructure` para documentação colaborativa e `docs/infrastructure/` como espelho versionado.

## Estrutura alvo

```text
rpg-op/
├── .cursor/
│   ├── agents/
│   ├── rules/
│   ├── skills/
│   └── hooks/
├── .sdlc/
│   ├── agents/
│   ├── commands/
│   ├── integrations/
│   ├── scripts/
│   ├── skills/
│   └── workflows/
├── apps/
│   ├── backend/
│   │   ├── app/
│   │   ├── scripts/
│   │   ├── pyproject.toml
│   │   └── README.md
│   └── frontend/
│       ├── src/
│       ├── package.json
│       ├── vite.config.ts
│       └── README.md
├── docs/
│   ├── infrastructure/
│   └── status/
├── infra/
│   ├── migrations/
│   ├── docker/
│   └── README.md
├── packages/
│   └── rpg_dsl/
├── specs/
├── tests/
│   ├── backend/
│   ├── frontend/
│   ├── integration/
│   └── e2e/
├── generated/
├── Makefile
└── pyproject.toml
```

## Responsabilidades

### `.cursor/`

Configuração da experiência Cursor IDE:

- Regras de contexto por área.
- Skills de entrada para workflows do agente.
- Adapters de agentes para IDE.
- Hooks locais de observabilidade e guardrails.

Não deve conter a configuração operacional canônica dos agentes. Essa responsabilidade é de `.sdlc/`.

### `.sdlc/`

Harness SDLC AI-native:

- Agentes canônicos e subagentes.
- Skills de engenharia.
- Commands e procedures reutilizáveis.
- Scripts locais de validação, integração e sincronização.
- Workflows de GitHub, Plane, CI e documentação.

### `apps/backend/`

Backend Python da aplicação, preferencialmente FastAPI:

- API BFF/domain em `app/`.
- Scripts operacionais locais em `scripts/`.
- Dependências controladas por `uv` via `pyproject.toml`.
- Banco local apenas em diretórios ignorados pelo git.
- Sem lógica de frontend, DSL ou infra acoplada.

### `apps/frontend/`

Frontend TypeScript com React + Vite:

- Código de UI em `src/`.
- Type checking explícito com `tsc`.
- Build de produção com `vite build`.
- Preview local com `vite preview`.
- Comunicação com backend por API versionada.

### `docs/`

Documentação versionada:

- Arquitetura e decisões técnicas.
- Status, pendências e guias operacionais.
- Espelhos de documentação do Plane quando necessário.

### `infra/`

Infraestrutura e operação:

- Migrations de banco em `infra/migrations/`.
- Docker, compose, IaC e manifests quando forem criados.
- Scripts de provisionamento que não pertencem ao backend ou ao frontend.

### `tests/`

Testes integrados ao monorepo:

- `tests/backend/` para API, domínio e persistência.
- `tests/frontend/` para componentes e comportamento de UI.
- `tests/integration/` para contratos entre frontend, backend, specs e generated.
- `tests/e2e/` para fluxos de usuário.

## Estado atual e transição

O repositório ainda possui caminhos legados:

- `backend/` contém o FastAPI atual.
- `apps/web/` contém o React + Vite atual.

Esses caminhos devem ser tratados como transição. A arquitetura alvo é:

- `backend/` -> `apps/backend/`
- `apps/web/` -> `apps/frontend/`

A migração física deve ser feita em tarefa própria, porque exige atualização coordenada de CI, hooks, docs, imports, configs de lint, scripts SDLC e comandos locais.

## Dependências Python com `uv`

Direção alvo:

- Usar `uv` no desenvolvimento local e CI.
- Preferir `pyproject.toml` por pacote Python.
- Usar `uv.lock` versionado para builds reprodutíveis.
- Usar workspace `uv` quando houver múltiplos pacotes Python ativos.
- Evitar novos fluxos baseados em `pip install -r` fora de transição.

Exemplo alvo para workspace:

```toml
[tool.uv.workspace]
members = [
    "apps/backend",
    "packages/rpg_dsl",
]
```

## Execução local

O `Makefile` na raiz é a entrada operacional padrão:

```powershell
make setup
make dev-backend
make dev-frontend
make test
make lint
make plane-sync-infrastructure
```

Enquanto a migração física não acontecer, o `Makefile` pode apontar para os caminhos legados por compatibilidade.

## Critérios de aceitação arquitetural

- A documentação de arquitetura no Plane `Infrastructure` e em `docs/infrastructure/project-architecture.md` está sincronizada.
- O repositório tem `Makefile` como ponto de entrada local.
- Novas decisões arquiteturais são registradas antes de alterar estrutura de diretórios.
- Novas tarefas Plane de arquitetura usam `context`, `changes`, `acceptance criteria` e `comments`.
- Nenhum novo código de aplicação deve ser introduzido em caminhos legados sem justificar a transição.
- A migração final atualiza CI, `.sdlc/config.yaml`, `.cursor/rules`, docs e comandos locais no mesmo PR.
