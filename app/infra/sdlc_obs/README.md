# sdlc-obs — SDLC Observability Tool

Lightweight, zero-dependency observability for the AI-Native SDLC pipeline.
Tracks precision, cost, time, tool success, hallucination rate, completion rate,
and regressions — per stage and per agent.

## Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Storage | SQLite | already in use, zero deps |
| Server | Python stdlib `http.server` | no install needed |
| Dashboard | Vanilla HTML/JS (inline) | no build step |
| Hooks | Python CLI scripts | callable from any agent or shell |

## Metrics Tracked

| Metric | How measured |
|--------|-------------|
| **Precision** | `completion_rate_pct` — completed runs / total runs per stage |
| **Cost** | `cost_usd` — sum of OpenAI token cost per run |
| **Time** | `avg_duration_sec` — wall-clock time from start to end of run |
| **Tool success rate** | `tool_calls_success / tool_calls_total` — MCP tool call outcomes |
| **Hallucination rate** | `hallucination_flag` — set manually or auto-detected (Doctor failure after claimed pass) |
| **Completion rate** | `completed` / `total_runs` — per stage and overall |
| **Regressions** | `regression_flag` — Doctor or tests failed after agent claimed success |

## Quick Start

```bash
# Initialize database
make obs-init

# Start dashboard server (default port 7700)
make obs-server

# Open in browser
open http://localhost:7700
```

## Recording a Run (CLI)

```bash
# 1. Start a run (at task begin)
python3 app/infra/sdlc_obs/hooks/pre_task.py \
  --task  "[AI][BACKEND] Add Plane endpoint" \
  --stage implementation \
  --agent implementer \
  --tags  "[AI]" "[BACKEND]"

# 2. Do the work...

# 3. End the run (at task completion)
python3 app/infra/sdlc_obs/hooks/post_task.py \
  --status    completed \
  --tokens-in 1200 --tokens-out 800 \
  --cost      0.0048 \
  --tools-total 5 --tools-ok 5 \
  --tests-pass  12 \
  --doctor    0
```

## Recording a Run (Python)

```python
from app.infra.sdlc_obs.collector import Collector

col = Collector()

# Start
run_id = col.start_run(
    task_name="[AI][BACKEND] Add Plane endpoint",
    stage="implementation",
    agent="implementer",
    task_tags=["[AI]", "[BACKEND]"],
)

# ... work ...

# End
col.end_run(
    run_id,
    completion_status="completed",
    tokens_input=1200, tokens_output=800,
    cost_usd=0.0048,
    tool_calls_total=5, tool_calls_success=5,
    tests_passed=12, doctor_exit_code=0,
)
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML dashboard |
| `GET /api/kpis` | Top-level KPIs (JSON) |
| `GET /api/summary` | Metrics grouped by stage + agent (JSON) |
| `GET /api/runs?limit=N&stage=S` | Recent runs (JSON) |

## Integration with Cursor Hooks

The `.cursor/hooks/pre-task.md` and `.cursor/hooks/post-task.md` procedures
include steps to call these hooks automatically. The agent emits metrics at the
beginning and end of every task.

## File Structure

```
app/infra/sdlc_obs/
├── README.md        ← this file
├── schema.sql       ← SQLite schema + metrics view
├── collector.py     ← metrics collector (read/write)
├── server.py        ← web server + HTML dashboard
├── data/            ← SQLite database (gitignored)
│   └── sdlc_obs.db
└── hooks/
    ├── __init__.py
    ├── emit.py      ← shared run_id state management
    ├── pre_task.py  ← CLI: open a run
    └── post_task.py ← CLI: close a run with metrics
```

## Hallucination Detection

A `hallucination_flag` is set when:
1. An agent claims Doctor passed but `doctor_exit_code` is `1`
2. An agent claims tests passed but `tests_failed > 0`
3. Manually flagged by a human reviewer via `--hallucination` in `post_task.py`

The hallucination rate is `sum(hallucination_flag) / total_runs × 100`.

## Adding New Metrics

1. Add columns to `schema.sql`
2. Add fields to `Collector.start_run()` or `Collector.end_run()`
3. Add CLI flags to `pre_task.py` or `post_task.py`
4. Update the dashboard in `server.py` (`_HTML`)
5. Run `make obs-init` to re-initialize the database
