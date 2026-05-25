# GitHub Integrator Adapter

YAML canônico: `.sdlc/agents/subagents/github-integrator.yaml`

Use para issues, branches, PRs, labels, Actions, checks e lifecycle GitHub do SDLC.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/github-sdlc/`.
- Prefira GitHub MCP quando disponível; use `gh` via scripts `.sdlc/scripts/gh-*.sh` como fallback.
- Nunca exponha tokens nem commite secrets.

## Exemplo

```text
Delegue ao github-integrator a abertura do PR SDLC para esta mudança.
```
