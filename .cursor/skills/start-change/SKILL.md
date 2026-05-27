# Skill: Start Change

> **Workflow authority:** `docs/sdlc/change-lifecycle.md`

## Purpose

Iniciar uma unidade de trabalho **antes de qualquer edição de código**, criando rastreabilidade Plane + branch gitflow.

## When to use

- Antes de implementar qualquer feature, bugfix ou infra
- Quando o usuário pede implementação (mesmo com urgência — gitflow não é opcional)
- **Somente após** `plane-task-creation` ter preenchido o card com plano completo

## Procedure

### 0. Verificar plano no Plane

Confirmar que o card `INVES-N` passou no gate de `.cursor/skills/plane-task-creation/SKILL.md`. Se o corpo só tem AC stubs → **parar** e completar plano.

### 1. Plane → **In Progress** (obrigatório)

**Antes** de criar branch ou editar código, mover o card para **In Progress**:

```bash
python3 .sdlc/scripts/plane_state.py in-progress --card INVES-N \
  --comment "start-change: branch feature/INVES-N-<slug>"
```

| Gate | Se falhar |
|------|-----------|
| Card existe no Plane | Parar — criar via `plane-task-creation` |
| Estado = In Progress | Parar — não implementar enquanto Todo/Backlog |

Se o card ainda não existe, criar via MCP (`.cursor/skills/plane-sdlc/SKILL.md`) já em **In Progress**.

### 2. Registrar número do card

Anotar `INVES-N` — obrigatório no nome do branch.

### 3. Criar branch a partir de develop

```bash
git checkout develop
git pull origin develop
git checkout -b feature/INVES-N-<slug>
```

Convenção: `.cursor/skills/branch-naming.md`

### 4. Observer pre-task (quando disponível)

```bash
python3 .sdlc/obs/hooks/pre_task.py --task "INVES-N: <title>" --stage implementation --agent implementer
```

Fallback se path legado: `python3 app/infra/sdlc_obs/hooks/pre_task.py`

### 5. Abrir gate mecânico (quando hooks presentes)

```bash
python3 .cursor/hooks/sdlc_gate.py open --card INVES-N --branch feature/INVES-N-<slug>
python3 .cursor/hooks/sdlc_gate.py status   # deve retornar open
```

### 6. Só então editar código

Nunca commitar em `develop` ou `main` durante implementação.

## Failure modes

| Situation | Action |
|-----------|--------|
| Card em Todo/Backlog durante implementação | **Parar** — `plane_state.py in-progress` primeiro |
| Plane indisponível | **Parar** — corrigir token; não criar backlog local |
| Sem card ID | **Parar** — criar card no Plane primeiro |
