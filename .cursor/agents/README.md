# Cursor Agents

Esta pasta é a camada de adaptação do Cursor para os agentes do SDLC.

## Fronteira

| Camada | Papel |
|--------|-------|
| `.sdlc/agents/` | Fonte canônica operacional: YAMLs com configuração, skills, tools, prompts e permissões. |
| `.cursor/agents/` | Instruções de uso no Cursor: quando chamar, como formular a delegação e onde está o YAML canônico. |
| `.cursor/rules/` | Contexto automático da IDE para arquivos e fluxos específicos. |

## Regra

Não duplique configuração operacional aqui. Se precisar alterar skills, tools, permissões, modelo ou `system_prompt`, edite o YAML em `.sdlc/agents/`.

## Adapters

- `dev-orchestrator.md` — entrada principal no chat do Cursor.
- `subagents/spec-author.md` — specs e DSL.
- `subagents/codegen-integrator.md` — validate, compile e integração.
- `subagents/eval-engineer.md` — evals e fixtures.
- `subagents/sdlc-doctor.md` — diagnóstico de saúde SDLC.
- `subagents/github-integrator.md` — GitHub lifecycle.
- `subagents/plane-integrator.md` — Plane lifecycle.
