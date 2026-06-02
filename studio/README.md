# SDLC Studio Foundation

`studio/` is the top-level home for SDLC Studio foundation material: human-facing documentation and descriptive schemas for modeling the repository's existing SDLC system.

SDLC Studio is not product code and is unrelated to `app/`. It operates over the real `.sdlc/` and `.cursor/` artifacts that already define workflows, agents, gates, skills, commands, hooks, rules, templates, and process authority.

## Purpose

- Provide a stable place for future Studio modeling documents and schemas.
- Describe workflow graphs, registry entities, and validation results without making them executable.
- Keep `.sdlc/` and `.cursor/` as the authoritative sources of truth.
- Support future UI or visualization planning without choosing a frontend, backend, runtime, or storage architecture.

## Contents

- `foundation-inventory.md` inventories the current Studio Foundation source
  areas and source-of-truth boundaries.
- `source-boundaries.md` extends the foundation inventory with stable boundary
  terminology for future Studio modeling work.
- `schemas/` contains descriptive YAML schema documents for future Studio data contracts.

## Boundaries

Studio Foundation does not implement UI, React Flow, TLDraw, command execution, compiler/runtime behavior, AI composition, LLM integration, persistence, backend services, frontend code, or distributed execution.

Do not add local tickets, backlog files, specs, or evidence records here. Plane remains the workboard source of truth, and delivery evidence belongs on Plane.
