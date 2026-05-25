# Specs — DSL Python (fonte da verdade)

Artefatos declarativos compilados por `rpg compile` → `generated/`.

## Layout (planejado)

```
specs/
├── templates/     # SheetSchema, CanvasSpec
├── agents/        # orchestrator, sheet_template_analyst
├── api/           # contratos BFF
└── evals/         # cenários LangSmith
```

## Regras

- Editável por humanos e por subagente `spec-author`
- Não colocar lógica de runtime (SQL, HTTP handlers)
- Ver `.sdlc/skills/dsl-authoring/SKILL.md`

## Status

Estrutura criada — implementação de `packages/rpg_dsl` pendente (S0).
