---
name: safe-refactor
description: >-
  Safe refactoring in RPG-OP — never edit generated/, minimal diffs, match repo conventions.
  Use when moving code, renaming, or integrating compile output.
---

# Safe refactor

## Forbidden

- Editing files under `generated/` directly
- Duplicating schema in backend + frontend + agent strings
- Large drive-by reformatting unrelated to the task

## Required

- Read surrounding code before changing backend/ or apps/web/
- Keep FastAPI routers thin; domain logic in app/models, fixtures
- SheetCanvas: presentation types in components/SheetCanvas

## Integrating compile output

```text
generated/pydantic/  → import in backend validation
generated/typescript/  → import in apps/web/src/types/ (future)
generated/agent_manifest/ → load in services/agent/ (future)
```

## Verify

```bash
cd backend && .venv/Scripts/python scripts/smoke_test.py
```
