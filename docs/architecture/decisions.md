# Architecture Decision Records

## Format

```markdown
## ADR-NNN — <title>

- **Date:** YYYY-MM-DD
- **Status:** proposed | accepted | superseded | deprecated
- **Context:** Why the decision was needed.
- **Decision:** What was decided.
- **Consequences:** What this means going forward.
- **Superseded by:** ADR-NNN (if applicable)
```

---

## ADR-001 — AI-Native SDLC as Project Operating System

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The project needs a structured approach to development that supports autonomous AI agents operating alongside human developers. Without a formal lifecycle model, agents risk making inconsistent, unsafe, or unverifiable changes.
- **Decision:** Adopt a 10-stage AI-Native SDLC model (ticket → requirements → architecture → implementation → validation → review → deployment → observability → incident → autofix) as the primary operating model. All agent activity is governed by `.sdlc/` configuration and `.cursor/` instructions.
- **Consequences:**
  - Every feature or fix must trace back to a stage and have explicit evidence.
  - Agents must load context before acting and validate after structural changes.
  - The Doctor is mandatory after structural changes.

---

## ADR-002 — Python as Primary Backend Language

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The `.env` and configuration imply Python tooling (`rpg_dsl`, `aiosqlite`, `pyproject.toml`). The team has Python expertise.
- **Decision:** Python is the primary backend language. New code follows PEP 8, uses type hints, and uses `pyproject.toml` for dependency management.
- **Consequences:** Frontend language is still TBD. Shared types may need serialization contracts (JSON Schema or Pydantic) for future cross-language use.

---

## ADR-003 — SQLite for Local Development

- **Date:** 2026-05-26
- **Status:** accepted
- **Context:** The `.env` defines `DATABASE_URL=sqlite+aiosqlite:///./data/rpg_op.db`. Using SQLite locally avoids Docker dependency for the database during the initialization phase.
- **Decision:** SQLite (`aiosqlite`) for local development. Production database target is TBD — will be decided when the first deployable service is defined. Use an ORM abstraction layer to minimize database-specific code and ease future migration.
- **Consequences:** Production database decision deferred. ORM must abstract the connection layer from day one.
