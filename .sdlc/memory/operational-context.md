# Operational Context Memory

> Runtime and environment context for Cursor agents. Update when infrastructure changes.

## Current State

**Status:** SDLC observability active — `app/infra/sdlc_obs/` implemented. No product application code.

## Workflow

**Source of truth:** `docs/sdlc/change-lifecycle.md`

## Environments

| Environment | Status       | Notes                          |
|-------------|--------------|--------------------------------|
| local       | active       | SQLite (obs), no product services |
| dev         | not_ready    | Pending product implementation |
| production  | not_ready    | Pending deployment setup       |

## Local Development

- Observability DB: `app/infra/sdlc_obs/data/`
- Python environment: managed via `pyproject.toml`
- No product containers yet

## SDLC Observability

- **Tool:** `app/infra/sdlc_obs/` (SQLite + Python stdlib server)
- **Dashboard:** `make obs-server` → http://localhost:7700
- **Metrics:** precision, cost, time, tool success, hallucination rate, completion rate, regressions
- **Hooks:** `.cursor/hooks.json` (sessionStart/stop) + `pre_task.py` / `post_task.py`

## External Services (Active)

| Service    | Purpose              | Configured Via          | MCP      |
|------------|----------------------|-------------------------|----------|
| GitHub     | Version control / PR | GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC | ✅ ativo |
| Plane      | Task management      | PLANE_API_KEY           | ✅ ativo  |
| OpenAI     | LLM inference        | OPENAI_API_KEY          | —        |

## Plane — Projeto ativo

- **Workspace:** `investments-sdlc` (`PLANE_WORKSPACE_SLUG`)
- **Project:** `investiments` (`PLANE_PROJECT_NAME`)
- **Card prefix:** `INVESTIMENTS-N` (branch: `feature/INVESTIMENTS-N-<slug>`)

Cards são criados no project `investiments` **antes** de qualquer edição de código.

## Key Configuration

- `AGENT_MODEL=openai:gpt-4.1-mini`
- `PLANE_WORKSPACE_SLUG=investments-sdlc`
- `PLANE_PROJECT_NAME=investiments`
- `GITHUB_REPOSITORY=DiegoCrassus/sdlc-ai`
