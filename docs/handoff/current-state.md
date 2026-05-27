# Current State — Handoff

> **Updated:** 2026-05-27  
> **Branch:** `develop`  
> **Phase:** SDLC operating system initialized — **no product application code**

## Summary

The repository contains the AI-Native SDLC harness (`.sdlc/`, `.cursor/`, `docs/sdlc/`, observability tool). Product boundaries `app/backend/` and `app/frontend/` are empty placeholders.

Previous market-data implementation was **removed** to restart from zero following `docs/sdlc/change-lifecycle.md`.

## Workflow (source of truth)

**Read first:** [docs/sdlc/change-lifecycle.md](../sdlc/change-lifecycle.md)

- Plane workspace: `investments-sdlc`
- Plane project: `investiments`
- Delivery: Plane card → feature branch → PR → CI green → merge `develop`

## What works today

- `make sdlc-doctor`
- `make sdlc-audit`
- `make obs-server` (observability dashboard)

## Governance (2026-05-27)

- **Tarefas:** somente Plane MCP (project `investiments`) — **nunca** `specs/` nem arquivos locais.
- Pasta `specs/` removida; referências no SDLC corrigidas.
- Skill: `.cursor/skills/plane-sdlc/SKILL.md`

## Next step

Criar epic + sub-tarefas no Plane via MCP; depois `start-change` por card.
