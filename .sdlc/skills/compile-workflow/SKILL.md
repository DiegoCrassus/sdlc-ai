---
name: compile-workflow
description: >-
  Run RPG-OP SDLC compile pipeline — validate specs, rpg compile, pytest, smoke.
  Use after spec changes or before PR merge.
---

# Compile workflow

## Order

1. `rpg validate specs/` (when CLI exists)
2. `rpg compile --target all`
3. Review `generated/` diff — do not hand-edit
4. `pytest backend/ -q`
5. `python backend/scripts/smoke_test.py` (API running)

## Targets

| Target | Output |
|--------|--------|
| pydantic | generated/pydantic/ |
| typescript | generated/typescript/ |
| agent_manifest | generated/agent_manifest/ |
| cursor_rules | .cursor/rules/generated-*.mdc |

## If rpg CLI missing

- Implement minimal change in `packages/rpg_dsl/` first
- Until then: manual hooks OK only with ADR note

## Fail closed

If compile would dirty `generated/` unexpectedly, stop and fix specs — do not patch generated files.
