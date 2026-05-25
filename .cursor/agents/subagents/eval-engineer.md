# Eval Engineer Adapter

YAML canônico: `.sdlc/agents/subagents/eval-engineer.yaml`

Use quando a mudança exigir cenários de avaliação, fixtures, smoke tests de agente ou gates LangSmith.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/deep-agent-harness/`.
- Prefira fixtures anonimizados e assertions objetivas.
- Mantenha evals versionados em `specs/evals/` ou `.sdlc/evals/`, conforme o escopo.

## Exemplo

```text
Delegue ao eval-engineer os evals smoke para este comportamento de agente.
```
