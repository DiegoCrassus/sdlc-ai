# PoC 0 — Fundação SDLC e contratos

**Status:** ✅ Concluído  
**Objetivo:** base técnica com fonte declarativa (`specs/`) e pipeline de compilação sem duplicar schema entre backend, frontend e agente.

## Contexto

Antes de valor ao mestre/jogador, o repositório precisava de contratos versionados e artefatos gerados automaticamente.

## Marcos entregues

| # | Marco | Evidência |
|---|-------|-----------|
| P0.1 | DSL instalável | `python -m rpg_dsl._cli` / `rpg validate specs/` |
| P0.2 | Specs de referência | `specs/templates/dnd5e_sheet.py`, `dnd5e_canvas.py` |
| P0.3 | Spec do subagente | `specs/agents/sheet_template_analyst.py` |
| P0.4 | Validate + compile | Artefatos em `generated/` |
| P0.5 | Targets gerados | Pydantic, JSON Schema, TypeScript, OpenAPI, manifest |
| P0.6 | CI local | `make validate` (`.sdlc/scripts/validate.sh`) |

## Critério de saída

✅ Spec versionada compila para artefatos consumíveis sem edição manual em `generated/`.

## Fora do escopo (intencional)

- UI de mesa
- PostgreSQL produção
- LLM em runtime

## Links

- [sdlc/ai-native.md](../sdlc/ai-native.md)
- [05-roadmap.md](../05-roadmap.md)
