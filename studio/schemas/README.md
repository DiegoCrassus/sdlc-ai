# Studio Schemas

This directory contains descriptive YAML schema documents for SDLC Studio Foundation.

The schemas model how Studio may describe existing `.sdlc/` and `.cursor/` artifacts. They are contracts for future indexing, visualization, and validation work, not executable workflow definitions.

## Schemas

- `graph.schema.yaml` describes a non-executable graph of SDLC entities and relationships.
- `workflow.schema.yaml` describes a workflow view built from stages, agents, gates, and transitions.
- `registry-entity.schema.yaml` describes a single referential registry entity.
- `validation-result.schema.yaml` describes validation output for Studio-readable checks.

## Non-Goals

These schemas do not define command behavior, runners, schedulers, LLM orchestration, UI components, API contracts, database models, or product runtime behavior.
