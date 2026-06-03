# AI Simulation Preview Prototype

Non-executing lifecycle preview for `INVES-70` (roadmap phase 8). Walks derived workflow IR and process authority without running agents, gates, or external systems. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → simulation_preview. CLI: `python -m studio.cli preview-simulation [--format text|json] [--root PATH] [--scenario SCENARIO]`.

Output: `simulation` (`derived_non_authoritative`, `execution_mode=non_executing_preview`), `summary`, `scenarios` (steps with `path_label` expected|blocked|unsupported), `lifecycle_map`. Non-goals: execution, persistence, Plane/GitHub. Implementation: `studio/simulation_preview.py`.
