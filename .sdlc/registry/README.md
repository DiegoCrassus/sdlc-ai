# SDLC Registry

`.sdlc/registry/` is a referential index for SDLC Studio Foundation.

The registry points to existing `.sdlc/` and `.cursor/` artifacts. It is not a new source of truth and must not copy lifecycle rules, gate policies, command bodies, prompt text, or template content.

## Files

- `index.yaml` describes the registry files and non-goals.
- `sdlc-artifacts.yaml` indexes existing SDLC artifacts.
- `cursor-artifacts.yaml` indexes existing Cursor artifacts.
- `relationships.yaml` records lightweight relationships between registered entities.

## Maintenance

Keep entries short and path-based. When an authoritative artifact changes, update the source file first and adjust registry references only when IDs, paths, or high-level relationships change.
