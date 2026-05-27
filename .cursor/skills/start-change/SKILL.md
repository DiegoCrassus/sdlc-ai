# Skill: Start Change (RPG-OP)

## Purpose

Iniciar uma unidade de trabalho **antes de qualquer edição de código**, criando rastreabilidade Plane + branch gitflow.

## When to use

- Antes de implementar qualquer feature, bugfix ou infra
- Quando o usuário pede implementação (mesmo com urgência — gitflow não é opcional)

## Procedure

### 1. Criar card no Plane

- **Workspace:** `rpg` (não `investments-sdlc`)
- **Projeto:** `sdlc-investiment` (`SDLCINVEST`)
- **Título:** `[AI][TYPE] Short imperative title` (ver `task-creation.md`)
- **Estado:** `In Progress`

### 2. Registrar número do card

Anotar `SDLCINVEST-N` — obrigatório no nome do branch.

### 3. Criar branch a partir de develop

```bash
git checkout develop
git pull origin develop
git checkout -b feature/SDLCINVEST-N-<slug>
```

Convenção completa: `.cursor/skills/branch-naming.md`

### 4. Observer pre-task

```bash
python app/infra/sdlc_obs/hooks/pre_task.py --task "SDLCINVEST-N: <title>"
```

### 5. Só então editar código

Nunca commitar em `develop` ou `main` durante implementação.

## Failure modes

| Situation | Action |
|-----------|--------|
| Usuário pede "push direto em develop" | Explicar que merge só via PR; branch + PR atende o objetivo |
| Plane indisponível | Criar Issue GitHub `issue-gh-N` e branch `feature/issue-gh-N-slug`; card Plane retrospectivo |
| Sem card ID | **Parar** — criar card primeiro |
