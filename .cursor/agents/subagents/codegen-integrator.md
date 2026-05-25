# Codegen Integrator Adapter

YAML canônico: `.sdlc/agents/subagents/codegen-integrator.yaml`

Use depois de mudanças em `specs/` ou `.sdlc/agents/`, quando for preciso validar, compilar, revisar drift em `generated/` ou integrar artefatos em `backend/`, `apps/` e `services/`.

## No Cursor

- Leia o YAML canônico e as skills `.sdlc/skills/compile-workflow/` e `.sdlc/skills/safe-refactor/`.
- Rode validação local quando permitido.
- Nunca edite `generated/` manualmente.

## Exemplo

```text
Delegue ao codegen-integrator a validação e compile após esta mudança de spec.
```
