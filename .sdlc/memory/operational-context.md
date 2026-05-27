# Operational Context Memory

> Runtime and environment context for Cursor agents. Update when infrastructure changes.

## Current State

**Status:** SDLC observability active — `app/infra/sdlc_obs/` implemented. No product services yet.

## Environments

| Environment | Status       | Notes                          |
|-------------|--------------|--------------------------------|
| local       | active       | SQLite, no containers yet      |
| dev         | not_ready    | Pending service implementation |
| production  | not_ready    | Pending deployment setup       |

## Local Development

- Database: SQLite at `./data/rpg_op.db`
- Python environment: managed via `pyproject.toml`
- No containers yet

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

- **Projeto:** sdlc-investiment (SDLCINVEST)
- **ID Plane:** 3f1a57f9-d1ad-42eb-a1d4-c7c2fa3e3cb5
- **Workspace:** rpg
- **Wiki pages criadas:** Home, SDLC Foundation Status, Roadmap, Architecture, Guia SDLC

## Key Configuration

- `AGENT_MODEL=openai:gpt-4.1-mini`
- `LANGSMITH_PROJECT=RPG`
- `PLANE_WORKSPACE_SLUG=rpg`
- `GITHUB_REPOSITORY=DiegoCrassus/sdlc-ai`
