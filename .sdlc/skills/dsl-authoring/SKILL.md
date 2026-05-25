---
name: dsl-authoring
description: >-
  Author RPG-OP DSL specs in specs/ — SheetSchema, CanvasSpec, SubAgent, API routes.
  Use when creating or changing specs/, packages/rpg_dsl/, or generated contracts.
---

# DSL authoring — RPG-OP

## When to use

- New sheet field, canvas region, or template analysis IR
- New product subagent spec (`sheet-template-analyst`)
- BFF route declarations in specs/api/

## IR locations

- `specs/templates/` — schema + canvas
- `specs/agents/` — product orchestrator + analysts
- `specs/api/` — BFF contracts
- `specs/evals/` — agent scenarios

## Rules

1. Python tipado; validável com mypy/ruff quando configurado.
2. Um ficheiro por domínio; nomes estáveis (`snake_case` keys).
3. `@Computed` para derivados determinísticos — não prompts.
4. Documentar breaking changes com versão incrementada.

## Example field

```python
# specs/templates/sheet_schema.py (future)
strength: int = Field(min=1, max=30, label="FOR", ui_group="attributes")
```

## References

- [docs/product/sheet-canvas.md](../../docs/product/sheet-canvas.md)
- [docs/sdlc/ai-native.md](../../docs/sdlc/ai-native.md)
