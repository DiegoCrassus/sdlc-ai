# Gates module

> **Data:** [`paths.yaml`](paths.yaml) · **Runtime:** `.sdlc/dsl/gate.py` + `.cursor/hooks/sdlc_gate_hook.py`

## Purpose

Mechanical **write permissions** by SDLC stage. The pre-write hook blocks edits to protected paths when the session gate is **closed** or the stage does not allow the path.

## When to read

| Situation | Action |
|-----------|--------|
| Before editing `app/` | Confirm `session-gate.json` → `gate_status: open` and stage = `implementation` |
| SDLC_META work on `.sdlc/` | Stage must be `sdlc_meta` or `planning` |
| Hook blocked your Write | Read `paths.yaml` → `gate_paths.stages.<stage>.allowed_prefixes` |
| Starting work | `python3 .sdlc/dsl/cli.py workflow start --card INVES-N --slug … --stage implementation` |

## Protected prefixes (always gated)

From `paths.yaml` → `gate_paths.protected_prefixes`:

- `app/backend/`, `app/frontend/`, `app/shared/`
- `pyproject.toml`

## Stage → allowed paths (summary)

| Stage | Typical allowed prefixes |
|-------|--------------------------|
| `planning` | `.sdlc/`, `.cursor/` |
| `architecture` | same as planning |
| `implementation` | `app/**`, `pyproject.toml`, `data/` |
| `sdlc_meta` | `.sdlc/`, `.cursor/`, `.github/`, `Makefile`, `AGENTS.md` |
| `validation` / `review` | read-heavy; see YAML for exceptions |

## Related modules

- [`../memory/README.md`](../memory/README.md) — `session-gate.json` fields (`card`, `branch`, `stage`)
- [`../gateways/README.md`](../gateways/README.md) — deterministic pre/post interaction harness
- [`../workboard/README.md`](../workboard/README.md) — Plane card must be In Progress before `workflow start`
- [`../workflows/README.md`](../workflows/README.md) — stage transitions

## Commands

```bash
python3 .sdlc/scripts/sdlc_gate.py status
python3 .sdlc/scripts/sdlc_gate.py check --path app/backend/src/foo.py
python3 .sdlc/dsl/cli.py workflow status
```

## Do not

- Bypass the hook with `--no-verify` or force writes — Orchestrator must run `workflow start` first
- Open gate on an **epic** card — only **child** cards (`INVES-N` with `[AI][BACKEND]` etc.)
