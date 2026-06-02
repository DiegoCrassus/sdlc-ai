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
- `graph-ir-contract.md` defines the descriptive, non-executable Graph IR
  contract for future Studio graph documents.
- `validation-result-ir-contract.md` defines the descriptive, non-executable
  Validation Result IR contract for future Studio validation records and Graph
  IR validation attachments.
- `compiler-validator-boundaries.md` defines the descriptive, non-executable
  Compiler/Validator phase boundary contract for future Studio derivation,
  validation, and report work.
- `schemas/` contains descriptive YAML schema documents for future Studio data contracts.

## Boundaries

Studio Foundation does not implement UI, React Flow, TLDraw, command execution, compiler/runtime behavior, validator execution, AI composition, LLM integration, persistence, backend services, frontend code, or distributed execution.

Do not add local tickets, backlog files, specs, or evidence records here. Plane remains the workboard source of truth, and delivery evidence belongs on Plane.
