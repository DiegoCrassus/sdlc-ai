# Comandos — SDLC

Índice de comandos locais e comandos de agente. Config declarativa: [commands.yaml](commands.yaml).

## Command Layer

`commands` agrupam skills, agentes e procedimentos reutilizáveis. Nem todo command
é um script executável: alguns são playbooks para o dev orchestrator delegar a
subagentes com contexto e saídas padronizadas.

| Command | Playbook | Agente |
|---------|----------|--------|
| `plane_backlog_plan` | [plane-backlog-plan.md](plane-backlog-plan.md) | `plane-integrator` |
| `technical_documentation` | [technical-documentation.md](technical-documentation.md) | `spec-author` |
| `architecture_documentation` | [architecture-documentation.md](architecture-documentation.md) | `spec-author` |
| `business_documentation` | [business-documentation.md](business-documentation.md) | `plane-integrator` |

## Validação local

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/validate.ps1` | validate + smoke API |
| `.sdlc/scripts/validate.sh` | idem (Unix) |

## Scripts Locais

### GitHub (gh)

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/gh-issue-intent.ps1` | Cria issue SDLC |
| `.sdlc/scripts/gh-pr-open.ps1` | Abre PR com template |
| `.sdlc/scripts/gh-sdlc-status.ps1` | Issues abertas por label |

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
