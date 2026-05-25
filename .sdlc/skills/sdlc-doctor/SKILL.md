---
name: sdlc-doctor
description: >-
  Diagnose RPG-OP SDLC AI-native health across specs, generated artifacts, gates,
  integrations, observability, documentation drift, and human blockers.
---

# SDLC DOCTOR

Use this skill when asked to evaluate the health, maturity, readiness, or drift
of the RPG-OP SDLC AI-native system.

## Scope

Check the engineering harness, not product gameplay behavior:

- `.sdlc/config.yaml` and `.sdlc/phases.yaml`
- `.sdlc/agents/` and `.sdlc/skills/`
- `.sdlc/scripts/validate.sh`
- `.cursor/hooks.json`, `.cursor/rules/`, and `.cursor/mcp.json`
- `specs/`, `packages/rpg_dsl/`, and `generated/`
- `.github/workflows/sdlc.yml` and PR/issue templates
- `docs/sdlc/ai-native.md`, `docs/status/pendencias-sdlc.md`, and `docs/status/pendencias-humanas.md`

## Diagnostic Order

1. Read `.sdlc/AGENTS.md`, `.sdlc/config.yaml`, and `docs/sdlc/ai-native.md`.
2. Inspect current declarative sources in `specs/` and `.sdlc/agents/`.
3. Compare `generated/` against the expected compiler targets without hand-editing generated files.
4. Run `.sdlc/scripts/validate.sh` when execution is allowed.
5. Check integration readiness for GitHub, Plane, LangSmith, Cursor hooks, and CI.
6. Review status docs for stale claims, blockers, and human-only tasks.

## Health Dimensions

- `spec_integrity`: specs exist, import cleanly, and match documented contracts.
- `compile_readiness`: `rpg validate` and `rpg compile --target all` are available or have a documented fallback.
- `generated_drift`: generated manifests, schemas, skills, and registry match declarative sources.
- `gate_readiness`: local validation, pytest, smoke tests, and GitHub Actions are configured.
- `integration_readiness`: MCP/CLI tokens and scripts are configured without exposing secrets.
- `observability`: Cursor hooks and LangSmith fallback logging are active.
- `documentation_freshness`: status docs match repository reality.
- `human_blockers`: actions requiring owner intervention are explicit and current.

## Report Format

Return a concise diagnostic:

```text
Status: HEALTHY | DEGRADED | BLOCKED
Maturity: L0-L4 with one-line rationale

Findings:
- [severity] area: evidence -> impact -> next action

Recommended next actions:
1. ...
2. ...
3. ...
```

Severity scale:

- `critical`: blocks SDLC execution or risks secrets/data loss.
- `high`: blocks PR readiness or causes generated/spec drift.
- `medium`: weakens reliability, observability, or documentation trust.
- `low`: cleanup or clarity improvement.

## Guardrails

- Do not edit `generated/` manually.
- Do not print secret values; only report whether required variables appear configured.
- Prefer evidence from files and command output over assumptions.
- Keep the report actionable and short enough to fit in a PR comment.
