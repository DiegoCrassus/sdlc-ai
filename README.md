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

**Human guide (full context):** [SDLC-GUIDE.md](SDLC-GUIDE.md)  
**Deep dive (papers P0/P1 + behavior):** [SDLC-DEEP-DIVE.md](SDLC-DEEP-DIVE.md)  
**Initialization spec:** [SDLC-basic.txt](SDLC-basic.txt)

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
   - `@sdlc-plan` — Plan a new ticket
   - `@sdlc-implement` — Implement a planned task
   - `@sdlc-review` — Review a PR or diff
   - `@sdlc-handoff` — Generate a handoff summary
   - `@sdlc-doctor` — Run the Doctor

## Basic Workflow

```
1. Plan      → sdlc-plan: convert ticket into structured plan
2. Architect → sdlc-plan / architect subagent: define technical approach
3. Implement → sdlc-implement: produce focused, tested code changes
4. Validate  → qa subagent: verify acceptance criteria with real evidence
5. Review    → sdlc-review: check correctness, security, maintainability
6. Handoff   → sdlc-handoff: generate stage transition summary
```

## Key Conventions

- Code is in English. Responses are in Portuguese.
- Small, reversible diffs are preferred over broad rewrites.
- No fake validation — always run tests and report real results.
- Docs are updated in the same commit as the code they describe.
- Doctor must pass after any structural change.

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [AI-Native SDLC Guide](docs/sdlc/ai-native-sdlc.md)
- [SDLC Workflows](docs/sdlc/workflows.md)
- [Validation Gates](docs/sdlc/gates.md)
- [Doctor Guide](docs/sdlc/doctor.md)
- [Current State](docs/handoff/current-state.md)

## License

MIT
