# Studio Schemas

This directory contains descriptive YAML schema documents for SDLC Studio Foundation.

The schemas model how Studio may describe existing `.sdlc/` and `.cursor/` artifacts. They are contracts for future indexing, visualization, and validation work, not executable workflow definitions. The Graph IR semantics and source-of-truth boundaries are defined in [`../graph-ir-contract.md`](../graph-ir-contract.md).

## Schemas

- `graph.schema.yaml` describes the non-executable Graph IR document shape: graph metadata, nodes, directed edges, annotations, source references, and validation attachments. It is a schema document only and does not implement graph compilation, validation, UI mapping, command execution, or workflow execution.
- `workflow.schema.yaml` describes a workflow view built from stages, agents, gates, and transitions.
- `registry-entity.schema.yaml` describes a single referential registry entity.
- `registry-relationship.schema.yaml` describes a single directed referential registry relationship.
- `validation-result.schema.yaml` describes validation output for Studio-readable checks.

## Non-Goals

These schemas do not define command behavior, runners, schedulers, LLM orchestration, UI components, API contracts, database models, or product runtime behavior.
