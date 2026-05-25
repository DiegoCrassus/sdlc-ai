# Dev Orchestrator Adapter

YAML canônico: `.sdlc/agents/dev-orchestrator.yaml`

Use este adapter quando o usuário pedir para conduzir o lifecycle SDLC, implementar uma mudança com spec-first, abrir issue/PR, diagnosticar gates ou coordenar subagentes.

## Responsabilidade No Cursor

- Traduzir a intenção do usuário para o fluxo `.sdlc/phases.yaml`.
- Delegar para subagentes canônicos em `.sdlc/agents/subagents/`.
- Manter a regra: specs e agentes em `.sdlc/` ou `specs/`; runtime em código; nunca editar `generated/` manualmente.

## Delegação

Leia o YAML canônico antes de operar. Para subagentes, consulte também o adapter correspondente em `.cursor/agents/subagents/`.

Exemplo:

```text
Use o dev-orchestrator para transformar esta intenção em issue, spec, validação e PR.
```
