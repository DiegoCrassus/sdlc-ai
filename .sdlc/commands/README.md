# Comandos — SDLC

Índice de comandos locais e comandos de agente. Config declarativa: [commands.yaml](commands.yaml).

## Command Layer

`commands` agrupam skills, agentes e procedimentos reutilizáveis. Nem todo command
é um script executável: alguns são playbooks para o dev orchestrator delegar a
subagentes com contexto e saídas padronizadas.

| Command | Playbook | Agente |
|---------|----------|--------|
| `start_change` | [start-change.md](start-change.md) | `dev-orchestrator` |
| `finish_change` | [finish-change.md](finish-change.md) | `github-integrator` |
| `plane_backlog_plan` | [plane-backlog-plan.md](plane-backlog-plan.md) | `plane-integrator` |
| `technical_documentation` | [technical-documentation.md](technical-documentation.md) | `spec-author` |
| `architecture_documentation` | [architecture-documentation.md](architecture-documentation.md) | `spec-author` |
| `business_documentation` | [business-documentation.md](business-documentation.md) | `plane-integrator` |

## Validação local

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/validate.sh` | validate + smoke API |
| `make validate` | atalho Makefile |

## Scripts Locais

### GitHub (gh)

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/gh-branch-start.sh` | Branch SDLC `feature/RPG-N` ou `bugfix/RPG-N` |
| `.sdlc/scripts/gh-issue-intent.sh` | Cria issue SDLC |
| `.sdlc/scripts/gh-pr-open.sh` | Abre PR com template |
| `.sdlc/scripts/gh-sdlc-status.sh` | Issues abertas por label |

Detalhes: [github.md](github.md)

## DSL

```bash
rpg validate specs/
rpg compile --target all
rpg eval run --suite smoke
```

## MCP (Cursor chat)

Sem CLI — use tools GitHub MCP:

- "Liste issues com label sdlc:ready"
- "Abra PR da branch atual fechando issue #N"
- "Mostre status do workflow SDLC no PR"

Skill: `.sdlc/skills/github-sdlc/SKILL.md`
