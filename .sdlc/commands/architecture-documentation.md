# Command: Architecture Documentation

## Objetivo

Documentar, revisar e manter a arquitetura do projeto RPG-OP com foco em uma estrutura sólida para Python + TypeScript.

A fonte de verdade colaborativa deve ser a documentação do Plane em `Infrastructure`, espelhada no repositório em `docs/infrastructure/project-architecture.md`.

## Quando Usar

- A estrutura do monorepo mudar.
- O backend, frontend, infra, migrations, testes ou harness SDLC forem reorganizados.
- Houver drift entre `README.md`, `docs/`, `.sdlc/config.yaml`, comandos locais e a documentação do Plane.
- Uma nova decisão arquitetural precisar ser registrada antes de implementação.

## Agente E Skills

- Agente preferencial: `spec-author`
- Apoio quando necessário: `plane-integrator`, `sdlc-doctor`, `codegen-integrator`
- Skills:
  - `.sdlc/skills/plane-sdlc/`
  - `.sdlc/skills/plane-task-creation/`
  - `.sdlc/skills/safe-refactor/`

## Fontes De Verdade

1. Plane Wiki ou Pages: `Infrastructure / Project Architecture`
2. Espelho versionado: `docs/infrastructure/project-architecture.md`
3. Execução local: `Makefile`
4. Registry do command: `.sdlc/commands/commands.yaml`

O Plane é a fonte colaborativa para decisões e contexto humano. O repositório mantém o espelho versionado para revisão por PR, rastreabilidade e automação.

## Arquitetura Alvo

O projeto deve ser organizado com estes blocos principais:

```text
rpg-op/
├── .cursor/
├── .sdlc/
├── apps/
│   ├── backend/
│   └── frontend/
├── docs/
│   └── infrastructure/
├── infra/
│   └── migrations/
├── packages/
├── specs/
├── tests/
├── generated/
└── Makefile
```

## Procedimento

1. Ler `docs/infrastructure/project-architecture.md` e a página Plane `Infrastructure / Project Architecture`.
2. Verificar a estrutura real do repositório contra a arquitetura alvo.
3. Documentar divergências explicitamente como transição, não como arquitetura final.
4. Atualizar `Makefile` quando comandos locais mudarem.
5. Garantir que Python use `uv` para ambiente, dependências e comandos locais.
6. Garantir que frontend use React + TypeScript + Vite dentro de `apps/frontend/`.
7. Garantir que backend use FastAPI/Python dentro de `apps/backend/`.
8. Garantir que infra, migrations e testes tenham ownership claro.
9. Sincronizar o espelho local para o Plane:

```bash
.sdlc/scripts/plane-sync-wiki-doc.sh docs/infrastructure/project-architecture.md "Infrastructure - Project Architecture"
```

10. Reportar o link da página Plane, arquivos alterados e qualquer pendência de migração.

## Guardrails

- Não tratar `backend/` e `apps/web/` como arquitetura final; eles são caminhos legados enquanto a migração não for concluída.
- Não editar `generated/` manualmente.
- Não criar documentação paralela fora de `docs/infrastructure/` ou Plane `Infrastructure`.
- Não criar tarefa Plane vaga; se uma migração for necessária, usar o modelo `context`, `changes`, `acceptance criteria`, `comments`.
- Não commitar tokens, `.env`, dumps locais ou bancos de desenvolvimento.

## Saída Esperada

```text
Arquitetura documentada:
- Plane: Infrastructure - Project Architecture -> <link ou pendência>
- Repo: docs/infrastructure/project-architecture.md

Estrutura local:
- Makefile atualizado
- infra/migrations documentado
- tests documentado

Pendências:
1. Migração backend/ -> apps/backend/
2. Migração apps/web/ -> apps/frontend/
3. Atualização de CI/configs quando a migração física acontecer
```
