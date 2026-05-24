# Comandos — SDLC + GitHub

Índice de comandos locais. Config declarativa: [commands.yaml](commands.yaml).

## Validação local

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/validate.ps1` | validate + smoke API |
| `.sdlc/scripts/validate.sh` | idem (Unix) |

## GitHub (gh)

| Script | Descrição |
|--------|-----------|
| `.sdlc/scripts/gh-issue-intent.ps1` | Cria issue SDLC |
| `.sdlc/scripts/gh-pr-open.ps1` | Abre PR com template |
| `.sdlc/scripts/gh-sdlc-status.ps1` | Issues abertas por label |

Detalhes: [github.md](github.md)

## DSL (futuro)

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
