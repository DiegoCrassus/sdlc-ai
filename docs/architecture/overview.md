# Architecture Overview

## Current Status

**Phase:** Initialization — no application code implemented yet.

The project structure has been initialized with the SDLC operating system. Application code will be added in future stages.

## System Boundaries

```
sdlc-ai/
├── app/
│   ├── frontend/    ← Future web frontend (framework TBD)
│   ├── backend/     ← Future Python API / service layer
│   ├── infra/       ← Future infrastructure-as-code
│   └── shared/      ← Shared utilities and types
├── .sdlc/           ← Machine-readable SDLC configuration
├── .cursor/         ← Cursor agent configuration
└── docs/            ← Human-readable documentation
```

## App Boundaries Convention

- **frontend** — User interface layer. No business logic.
- **backend** — Business logic, API, data access. No rendering logic.
- **infra** — Infrastructure definitions (IaC, containers, cloud config).
- **shared** — Types, constants, and utilities shared between frontend and backend.

## Data Layer

- **Local development:** SQLite (`./data/rpg_op.db`)
- **Production target:** TBD
- ORM: TBD (likely SQLAlchemy with async support, given `aiosqlite` in `.env`)

## Key Technology Decisions

| Area        | Decision        | Status   | Notes                              |
|-------------|-----------------|----------|------------------------------------|
| Backend     | Python          | decided  | Primary language                   |
| Database    | SQLite (local)    | decided | Production target TBD              |
| Frontend    | TBD             | pending  | Decide when frontend work starts   |
| Deployment  | TBD             | pending  | Kubernetes or serverless TBD       |
| Auth        | TBD             | pending  | Decide when user features start    |

## Design Principles

1. **Vertical slices** — Build full end-to-end features, not horizontal layers.
2. **Observability first** — Every component emits logs and metrics from day one.
3. **Small diffs** — Prefer reversible, scoped changes over large rewrites.
4. **SDLC-driven** — No code without a plan and acceptance criteria.
