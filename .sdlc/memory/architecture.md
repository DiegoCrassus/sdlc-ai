# Architecture Memory

> Persistent architectural context for Cursor agents. Update when significant decisions are made.

## Current State

**Status:** Dual product surface in `app/` — MarketPulse (financial dashboard) + Studio Service (SDLC control plane, architecture complete INVES-77).

| Package | Purpose | Status |
|---------|---------|--------|
| `app/backend/` | MarketPulse API (`marketpulse`) | Implemented |
| `app/frontend/` | MarketPulse UI | Implemented |
| `app/studio-backend/` | Studio Service API (`studio_service`) | Architecture only — INVES-78 |
| `app/studio-frontend/` | Studio Service UI | Architecture only — INVES-79 |
| `app/infra/sdlc_obs/` | SDLC metrics SQLite + dashboard | Implemented |
| `studio/` | Foundation engine (compile, validate, canvas) | Implemented (S0) |
| `app/shared/` | Cross-product JSON schemas / TS types | MarketPulse-focused |

## Studio Service boundaries (INVES-77)

- **Doc:** `docs/architecture/studio-service-platform.md`
- **ADR:** ADR-009 in `docs/architecture/decisions.md`
- API prefix `/studio/*`, ports 8100 (API) + 5174 (UI)
- Mutations: propose → review → git/Plane apply (no silent writes) — **frozen contract:** [§ Propose-only mutation contract](#propose-only-mutation-contract-s4--inves-84) (INVES-84)
- Observability: `StudioEvent` envelope over SSE; sources = sdlc_obs + gateway hooks + handoff + gate
- React Flow: renders derived canvas; layout is UI-local only

## Propose-only mutation contract (S4 / INVES-84)

> **Status:** Accepted (INVES-84). Blocks S4 backend/frontend implementation children.  
> **ADR:** [ADR-010](../../docs/architecture/decisions.md#adr-010--studio-s4-propose-only-mutation-contract)  
> **Policy reference:** `.sdlc/gateways/policy.yaml` → `studio_proposals`  
> **Platform routes:** `docs/architecture/studio-service-platform.md` §3 S4, §5

### Principle

Studio **never** applies authoritative writes. It builds **proposals** (patch previews + dry-run results). Apply is always external: Plane child card → `workflow start` → feature branch → commit → PR → merge (`.sdlc/process/change-lifecycle.md`).

**Silent write prohibition (AC-3):** No API route, background job, or UI action may write under allowed prefixes without an operator explicitly applying via git on an open gate. No `POST .../apply`, no `git commit`/`push`/`merge` endpoints, no Plane state mutation from Studio.

### Allowed target path prefixes (AC-1)

Proposals may only touch paths under these prefixes. Any other path is rejected at proposal creation (`422` + `path_not_allowed`).

| Prefix | Builder `kind` | Notes |
|--------|----------------|-------|
| `.sdlc/workflows/` | `workflow` | Transitions, workflow graphs |
| `.sdlc/stages/` | `workflow` | Lifecycle stage YAML only via workflow builder |
| `.sdlc/pipeline/` | `workflow` | Agent roster bindings |
| `.sdlc/manifest/` | `workflow` | Catalog entries when tied to workflow change |
| `.sdlc/gates/` | `workflow` | `paths.yaml` — high risk; Doctor mandatory |
| `.cursor/agents/` | `agent` | `*.md` agent definitions |
| `.cursor/rules/` | `rule` | `*.mdc` rules |
| `.cursor/skills/` | `skill` | `**/SKILL.md` and skill markdown |
| `.cursor/commands/` | `command` | `*.md` slash commands |

**Explicit denylist** (never in `target_paths`, reject at create):

| Prefix / path | Reason |
|---------------|--------|
| `.sdlc/memory/` | Runtime session/handoff — not authoring |
| `.sdlc/templates/plane/` | Evidence templates — Plane workflow only |
| `.cursor/hooks/`, `.cursor/hooks.json` | Enforcement surface — SDLC_META card + human only |
| `.cursor/mcp.json`, `.cursor/mcp.json.example` | Secrets / local config |
| `app/`, `pyproject.toml`, `Makefile`, `.github/`, `AGENTS.md`, `docs/`, `specs/`, `studio/` | Product/engine — not Studio builder scope |

Alignment with mechanical gate: `.sdlc/gates/paths.yaml` `planning` / `architecture` / `sdlc_meta` stages allow `.sdlc/` + `.cursor/`; Studio allowlist is a **strict subset** (denylist above).

### Patch format (frozen for implementer)

| Field | Value |
|-------|-------|
| `patch_format` (wire) | `unified_diff` (required for API response and human apply) |
| `patch_body` | Standard unified diff text, one or more files |
| Builder input | `structured_ops` (optional, server-side only) → compiled to `unified_diff` |

**`structured_ops` schema** (request body on `POST /studio/proposals`):

```json
{
  "kind": "workflow | agent | rule | skill | command",
  "title": "human label",
  "target_paths": [".sdlc/workflows/transitions.yaml"],
  "ops": [
    {
      "op": "replace_block | insert_after | delete_lines | create_file",
      "path": "relative/repo/path",
      "anchor": "optional regex or line id",
      "content": "new file or replacement body"
    }
  ],
  "simulated_gate": {
    "stage": "planning | architecture | sdlc_meta",
    "card": "INVES-N"
  }
}
```

- YAML targets (`.sdlc/**/*.yaml`): ops compile via parse → mutate → `yaml.dump` → diff against repo file; invalid YAML fails validate with exit **1**.
- Markdown targets (`.cursor/**/*.md`, `*.mdc`): ops compile to line-oriented unified diff; `create_file` only if parent dir exists and path is allowlisted.

**Authority badge:** every proposal includes `authority_badge: proposed_non_authoritative` (constant).

**Storage:** in-memory map or temp dir under `.gitignore` (e.g. `.studio/proposals/`); TTL 24h; never committed.

### Dry-run sequence (AC-2)

Mandatory order after `POST /studio/proposals`. Each step returns `exit_code` **0** (pass) or **1** (fail). UI shows cumulative status; failed step blocks “ready to apply” banner.

| Step | API | Mechanism | Pass (`exit_code: 0`) | Fail (`exit_code: 1`) |
|------|-----|-----------|------------------------|------------------------|
| 1 Validate | `POST /studio/proposals/{id}/validate` | Copy proposed files into temp tree; run `studio` compile + validate | No engine errors on proposed IR | Validation errors / broken refs |
| 2 Doctor | `POST /studio/proposals/{id}/doctor` | Materialize temp workspace; `make sdlc-doctor` subprocess | Doctor process exit 0 | Doctor exit 1 or timeout |
| 3 Gateway check | `POST /studio/proposals/{id}/gateway-check` | For each `target_path`, call `.sdlc/dsl/gate.check_write` with `simulated_gate.stage`; optional overlay of open `session-gate.json` | All paths allowed for simulated stage | Any path denied |

Response shape (all three steps):

```json
{
  "proposal_id": "uuid",
  "step": "validate | doctor | gateway-check",
  "exit_code": 0,
  "summary": "short human message",
  "details": []
}
```

**Doctor temp workspace:** `tempfile.mkdtemp` + copy repo `.sdlc/`, `.cursor/` (allowlisted only) + apply proposed file contents → run doctor → delete tree. No writes to real repo.

### Gateway check mandatory (AC-4)

- Step 3 is **required** before the UI may show an apply checklist or copy-patch CTA.
- No bypass flag in S4 MVP.
- `gateway-check` must evaluate **every** `target_path` and return per-path `{ "path", "allowed", "reason", "gate_status", "stage" }`.
- If `session-gate.json` is `closed`, simulation uses `simulated_gate.stage` from the proposal request; UI warns that real apply still requires `workflow start`.
- Reject proposal create if any `target_path` fails allowlist (fail-closed before dry-run).

Implementer reuses `gate.check_write` from `.sdlc/dsl/gate.py` — do not duplicate policy logic in Studio.

### Apply path (operator, outside Studio)

```text
1. Plane: child card INVES-M in progress (not epic)
2. CLI: python3 .sdlc/dsl/cli.py workflow start --card INVES-M --stage <planning|architecture|sdlc_meta> --slug <slug>
3. Git: feature/INVES-M-<slug> checked out; session-gate.json open with matching stage
4. Apply patch_body (patch(1), IDE, or Task(Implementer))
5. make sdlc-doctor (on real repo)
6. commit → push → PR → QA → DevOps merge → workflow finish
```

Studio may deep-link to Plane card and show read-only gate/handoff after apply; it does not perform steps 2–6.

### API surface (implementer checklist)

| Route | Allowed |
|-------|---------|
| `POST /studio/proposals` | Yes — create preview |
| `GET /studio/proposals/{id}` | Yes |
| `POST .../validate`, `.../doctor`, `.../gateway-check` | Yes — dry-run only |
| `DELETE /studio/proposals/{id}` | Yes — discard |
| `POST /studio/proposals/{id}/apply` | **Forbidden** |
| Any route writing `.sdlc/` / `.cursor/` without proposal id | **Forbidden** |

### Trade-offs

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Unified diff only | Familiar, git-native apply | Weak for binary | **Wire format** |
| Structured ops + compile | Builder-friendly | Needs compiler | **Input format** |
| API apply with gate token | One-click | Bypass risk | **Rejected** |
| In-repo proposal files | Auditable | Authority leak | **Rejected** — temp/gitignore only |

### Implementation breakdown (S4 children)

| Module | Responsibility |
|--------|----------------|
| `studio_service/schemas/proposals.py` | Pydantic: Proposal, StructuredOp, DryRunResult |
| `studio_service/services/mutation.py` | Allowlist, op→diff, proposal store |
| `studio_service/services/doctor_runner.py` | Temp workspace doctor |
| `studio_service/api/routes/proposals.py` | S4 routes |
| `studio-frontend` builder routes | Call proposals API; banner + dry-run panel |

### Open questions (resolved for S4)

- Patch wire format: **unified_diff** (ADR-010).
- Gateway check: **mandatory**, uses `gate.check_write` + `simulated_gate.stage`.

## MarketPulse boundaries

- `app/backend/src/marketpulse/` — FastAPI, `/api/v1/*`, port 8000
- `app/frontend/` — Vite SPA, port 5173
- ADRs: ADR-004..008, `docs/architecture/marketpulse-api-providers.md`

## Known Constraints

- Python primary backend language
- SQLite for local dev (product DB + sdlc_obs)
- Plane + GitHub MCP for workflow
- Studio never bypasses `.cursor/hooks` write gate

## Open Questions

- pyproject packaging for `studio_service` — optional `[studio]` extra vs dedicated editable install (INVES-78)
- `sdlc_events` SQLite table vs JSONL for gateway events (S3 — prefer table for timeline queries)

## Design Principles

- Vertical slices over horizontal layers
- Small, reversible changes
- Observability from the start
- SDLC-driven development
- Derived views labeled; authoritative sources unchanged
