# sdlc-ai

AI-Native SDLC platform — a project operating system for teams where AI agents and human developers work together across the full software development lifecycle.

> This repository is built using the same SDLC model it implements.

## Project Structure

```
.
├── .cursor/          ← Cursor agent configuration (rules, commands, skills, subagents, hooks)
├── .sdlc/            ← SDLC configuration (YAML + Python DSL)
├── docs/             ← Human-readable documentation
├── app/              ← MarketPulse application code
│   ├── frontend/     ← React/Vite web frontend
│   ├── backend/      ← FastAPI Python API
│   ├── infra/        ← SDLC observability + terraform placeholders
│   ├── shared/       ← Shared types and utilities
│   └── Makefile      ← One-command local dev (make start)
├── Makefile          ← SDLC and development commands
├── pyproject.toml    ← Python project configuration
└── README.md         ← This file
```

## Run the app locally

The MarketPulse app (FastAPI backend + React/Vite frontend) runs with a single command:

```bash
cd app
make start
```

This installs dependencies if needed and runs the backend (http://127.0.0.1:8000/docs)
and frontend (http://127.0.0.1:5173) together; press `Ctrl+C` to stop both.
See [docs/infrastructure/local-development.md](docs/infrastructure/local-development.md)
for the full list of targets and configurable variables.

## SDLC retest (app reset)

The `app/` tree was reset to allow a **full greenfield SDLC run** in a new agent session, which produced the MarketPulse app now under `app/backend/` and `app/frontend/`.

**SDLC process authority:** [.sdlc/process/master-workflow.md](.sdlc/process/master-workflow.md)
**Change lifecycle authority:** [.sdlc/process/change-lifecycle.md](.sdlc/process/change-lifecycle.md)
**SDLC module index:** [.sdlc/README.md](.sdlc/README.md)

Start with: *Build a product called Investment Radar …* — see [docs/handoff/current-state.md](docs/handoff/current-state.md).

Prior delivery reference: [docs/product/investment-radar-runbook.md](docs/product/investment-radar-runbook.md) · [docs/architecture/investment-radar-api.md](docs/architecture/investment-radar-api.md).

## Run the SDLC Doctor

The Doctor validates the repository structure, YAML configuration, and documentation:

```bash
make sdlc-doctor
```

Expected output on a clean repository:
```
[PASS] Required directory exists: .cursor
[PASS] Required file exists: .sdlc/sdlc.yaml
...
Doctor summary: N passed, N warnings, 0 failed
```

Exit code `0` = all required checks pass. Exit code `1` = failures found.

## How to Use Cursor with This SDLC

1. **Open the repository in Cursor.** The `.cursor/` directory is automatically loaded.

2. **Before starting any task**, load context:
   - `.sdlc/sdlc.yaml`
   - `.sdlc/memory/architecture.md`
   - `.sdlc/memory/business-rules.md`

3. **Use the SDLC commands** in Cursor chat:
   - `@sdlc-run` — Run the orchestrated SDLC pipeline
   - `@sdlc-review` — Review a PR or diff
   - `@sdlc-doctor` — Run the Doctor

## Basic Workflow

```
1. Run       → sdlc-run: start or resume the orchestrated pipeline
2. Plan      → planner subagent: create Plane epic and child cards
3. Architect → architect subagent: define technical approach
4. Implement → implementer subagent: produce focused code changes
5. Validate  → qa subagent: verify acceptance criteria with real evidence
6. Review    → reviewer/devops subagents: approve, PR, merge, and finish
```

## Key Conventions

- Code is in English. Responses are in Portuguese.
- Small, reversible diffs are preferred over broad rewrites.
- No fake validation — always run tests and report real results.
- Docs are updated in the same commit as the code they describe.
- Doctor must pass after any structural change.

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [SDLC Master Workflow](.sdlc/process/master-workflow.md)
- [Change Lifecycle](.sdlc/process/change-lifecycle.md)
- [SDLC Module Index](.sdlc/README.md)
- [Current State](docs/handoff/current-state.md)

## License

MIT
