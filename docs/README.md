# docs — Human-Readable Project Documentation

This directory contains human-readable product, architecture, infrastructure, operations, roadmap, and handoff documentation for the `sdlc-ai` project.

## Structure

| Directory        | Purpose                                          |
|------------------|--------------------------------------------------|
| `architecture/`  | System design, boundaries, and decisions         |
| `infrastructure/`| Local dev, deployment, and environment setup     |
| `handoff/`       | State summaries and stage transition records     |
| `roadmap/`       | Planned work and milestones                      |
| `operations/`    | Observability, incidents, and maintenance        |
| `product/`       | Product runbooks and legacy discovery material   |

## Conventions

- Docs reflect the **current state**, not aspirational state.
- Use "TBD" or "placeholder" for future content — do not leave empty sections.
- Update docs in the same commit as the code change they describe.
- Handoff summaries go in `handoff/current-state.md`.
- ADRs (Architecture Decision Records) go in `architecture/decisions.md`.
- SDLC process, guides, references, and templates live under `.sdlc/`, not `docs/`.
- Do not create `docs/sdlc/`, `docs/helper/`, or `docs/references/`; Doctor treats those as structural drift.
