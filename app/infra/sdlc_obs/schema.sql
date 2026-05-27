-- SDLC Observability Schema
-- SQLite — zero external dependencies

CREATE TABLE IF NOT EXISTS sdlc_runs (
    -- Identity
    id            TEXT PRIMARY KEY,
    task_name     TEXT NOT NULL,          -- e.g. "[AI][BACKEND] Add Plane endpoint"
    stage         TEXT NOT NULL,          -- ticket | requirements | architecture | implementation | validation | review | deployment | observability | incident | autofix
    agent         TEXT NOT NULL,          -- planner | architect | implementer | qa | reviewer | devops | doctor

    -- Timing
    started_at    REAL NOT NULL,          -- unix timestamp
    ended_at      REAL,
    duration_ms   INTEGER,

    -- Cost (OpenAI tokens)
    tokens_input  INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    cost_usd      REAL DEFAULT 0.0,

    -- Tool calls (MCP)
    tool_calls_total   INTEGER DEFAULT 0,
    tool_calls_success INTEGER DEFAULT 0,
    tool_calls_failed  INTEGER DEFAULT 0,

    -- Validation signals
    doctor_exit_code   INTEGER,           -- 0=pass 1=fail NULL=not run
    tests_passed       INTEGER DEFAULT 0,
    tests_failed       INTEGER DEFAULT 0,

    -- Quality flags
    completion_status  TEXT DEFAULT 'unknown',  -- completed | failed | escalated | abandoned
    hallucination_flag INTEGER DEFAULT 0,       -- 1 if fabricated result detected
    regression_flag    INTEGER DEFAULT 0,       -- 1 if Doctor/tests failed post-implementation

    -- Context
    task_tags     TEXT DEFAULT '[]',      -- JSON: ["[AI]","[BACKEND]"]
    notes         TEXT DEFAULT '',

    created_at    TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_runs_stage   ON sdlc_runs(stage);
CREATE INDEX IF NOT EXISTS idx_runs_agent   ON sdlc_runs(agent);
CREATE INDEX IF NOT EXISTS idx_runs_created ON sdlc_runs(created_at);

-- Aggregated metrics view
CREATE VIEW IF NOT EXISTS sdlc_metrics AS
SELECT
    stage,
    agent,
    COUNT(*)                                                    AS total_runs,
    SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) AS completed,
    ROUND(
        100.0 * SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 1
    )                                                           AS completion_rate_pct,
    ROUND(AVG(duration_ms) / 1000.0, 1)                        AS avg_duration_sec,
    ROUND(SUM(cost_usd), 4)                                     AS total_cost_usd,
    SUM(tool_calls_total)                                       AS tool_calls_total,
    SUM(tool_calls_success)                                     AS tool_calls_success,
    ROUND(
        100.0 * SUM(tool_calls_success) / NULLIF(SUM(tool_calls_total), 0), 1
    )                                                           AS tool_success_rate_pct,
    ROUND(
        100.0 * SUM(hallucination_flag) / COUNT(*), 1
    )                                                           AS hallucination_rate_pct,
    SUM(regression_flag)                                        AS regressions,
    SUM(tests_passed)                                           AS tests_passed,
    SUM(tests_failed)                                           AS tests_failed
FROM sdlc_runs
GROUP BY stage, agent;
