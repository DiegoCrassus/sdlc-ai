# SDLC Registry

`.sdlc/registry/` is a referential index for SDLC Studio Foundation.

The registry points to existing `.sdlc/` and `.cursor/` artifacts. It is not a new source of truth and must not copy lifecycle rules, gate policies, command bodies, prompt text, or template content.

## Files

- `index.yaml` describes the registry files and non-goals.
- `sdlc-artifacts.yaml` indexes existing SDLC artifacts.
- `cursor-artifacts.yaml` indexes existing Cursor artifacts.
- `relationships.yaml` records lightweight relationships between registered entities.

## Entity Invariants

Each registry entity is a pointer to one existing repository artifact:

- `id` uses a stable namespace: `sdlc.*` for `.sdlc/` artifacts and `cursor.*` for `.cursor/` artifacts.
- `path` stays under `.sdlc/` or `.cursor/` and matches `source_system`.
- `source_system` matches both the `id` namespace and the path prefix.
- `source_module` names the owning source area only; it does not redefine that area's behavior.
- `summary` is short and referential. It explains why the artifact is indexed without copying authoritative content.
- `tags` classify the entry with lightweight labels.

Relationship records use registry entity IDs in `from` and `to`. `source_refs` must point to real `.sdlc/` or `.cursor/` paths that ground the relationship.

## Source Boundaries

`.sdlc/` remains authoritative for process, lifecycle, gates, workflows, templates, scripts, doctor checks, and handoff state. `.cursor/` remains authoritative for agents, skills, rules, commands, hooks, and Cursor configuration.

The registry must not store rule bodies, lifecycle bodies, gate policies, command bodies, prompt text, hook logic, templates, workflow definitions, delivery evidence, generated outputs, or runtime behavior.

## Maintenance

Keep entries short and path-based. When an authoritative artifact changes, update the source file first and adjust registry references only when IDs, paths, or high-level relationships change.

Before handoff, parse changed YAML files and verify that artifact paths, source systems, unique IDs, relationship targets, and relationship source references remain consistent with the invariants above.
