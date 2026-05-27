# Skill: Start Change

> **Workflow authority:** `docs/sdlc/change-lifecycle.md`

## Purpose

Iniciar uma unidade de trabalho **antes de qualquer edição de código**, criando rastreabilidade Plane + branch gitflow.

## When to use

- Antes de implementar qualquer feature, bugfix ou infra
- Quando o usuário pede implementação (mesmo com urgência — gitflow não é opcional)

## Procedure

### 1. Criar card no Plane (MCP — obrigatório)

Seguir `.cursor/skills/plane-sdlc/SKILL.md`.

- **Workspace:** `investments-sdlc` (`PLANE_WORKSPACE_SLUG`)
- **Project:** `investiments` (`PLANE_PROJECT_NAME`)
- **Título:** `[AI][TYPE] Short imperative title` (ver `task-creation.md`)
- **Descrição:** story, scope, non-goals, AC, DoD (no corpo do card — **nunca** em `specs/`)
- **Estado:** `In Progress`

### 2. Registrar número do card

Anotar `INVESTIMENTS-N` — obrigatório no nome do branch.

### 3. Criar branch a partir de develop

```bash
git checkout develop
git pull origin develop
git checkout -b feature/INVESTIMENTS-N-<slug>
```

Convenção completa: `.cursor/skills/branch-naming.md`

### 4. Observer pre-task

```bash
python app/infra/sdlc_obs/hooks/pre_task.py --task "INVESTIMENTS-N: <title>"
```

### 5. Só então editar código

Nunca commitar em `develop` ou `main` durante implementação.

## Failure modes

| Situation | Action |
|-----------|--------|
| Usuário pede "push direto em develop" | Explicar que merge só via PR; branch + PR atende o objetivo |
| Plane indisponível | **Parar** — corrigir MCP/token; não criar backlog local nem `specs/` |
| Sem card ID | **Parar** — criar card no Plane via MCP primeiro |
