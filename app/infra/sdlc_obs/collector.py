"""
SDLC Observability Collector
-----------------------------
Records metrics for every SDLC stage run to a local SQLite database.
Zero external dependencies — uses only the Python standard library.

Usage:
    from app.infra.sdlc_obs.collector import Collector

    col = Collector()
    run_id = col.start_run(task_name="[AI][BACKEND] Add Plane endpoint",
                           stage="implementation", agent="implementer")
    # ... work happens ...
    col.end_run(run_id, completion_status="completed",
                tokens_input=1200, tokens_output=800,
                tool_calls_total=5, tool_calls_success=5,
                tests_passed=12, doctor_exit_code=0)
"""

import json
import sqlite3
import time
import uuid
from pathlib import Path

_DEFAULT_DB = Path(__file__).parent / "data" / "sdlc_obs.db"
_SCHEMA = Path(__file__).parent / "schema.sql"

VALID_STAGES = {
    "ticket", "requirements", "architecture", "implementation",
    "validation", "review", "deployment", "observability", "incident", "autofix",
}

VALID_AGENTS = {
    "planner", "architect", "implementer", "qa",
    "reviewer", "devops", "doctor", "observer",
}

VALID_STATUSES = {"completed", "failed", "escalated", "abandoned", "unknown"}


class Collector:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else _DEFAULT_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ── public API ─────────────────────────────────────────────────────────

    def start_run(
        self,
        task_name: str,
        stage: str,
        agent: str,
        task_tags: list | None = None,
        notes: str = "",
    ) -> str:
        """Open a new run. Returns the run_id to pass to end_run()."""
        if stage not in VALID_STAGES:
            raise ValueError(f"Unknown stage: {stage!r}. Valid: {VALID_STAGES}")
        if agent not in VALID_AGENTS:
            raise ValueError(f"Unknown agent: {agent!r}. Valid: {VALID_AGENTS}")

        run_id = str(uuid.uuid4())
        with self._conn() as db:
            db.execute(
                """
                INSERT INTO sdlc_runs
                    (id, task_name, stage, agent, started_at, task_tags, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (run_id, task_name, stage, agent, time.time(),
                 json.dumps(task_tags or []), notes),
            )
        return run_id

    def end_run(
        self,
        run_id: str,
        completion_status: str = "completed",
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        tool_calls_total: int = 0,
        tool_calls_success: int = 0,
        tool_calls_failed: int = 0,
        doctor_exit_code: int | None = None,
        tests_passed: int = 0,
        tests_failed: int = 0,
        hallucination_flag: bool = False,
        regression_flag: bool = False,
        notes: str = "",
    ) -> None:
        """Close a run and record its outcome metrics."""
        if completion_status not in VALID_STATUSES:
            raise ValueError(f"Unknown status: {completion_status!r}")

        ended_at = time.time()
        with self._conn() as db:
            row = db.execute(
                "SELECT started_at FROM sdlc_runs WHERE id = ?", (run_id,)
            ).fetchone()
            if not row:
                raise ValueError(f"Run not found: {run_id!r}")

            duration_ms = int((ended_at - row[0]) * 1000)
            db.execute(
                """
                UPDATE sdlc_runs SET
                    ended_at            = ?,
                    duration_ms         = ?,
                    completion_status   = ?,
                    tokens_input        = ?,
                    tokens_output       = ?,
                    cost_usd            = ?,
                    tool_calls_total    = ?,
                    tool_calls_success  = ?,
                    tool_calls_failed   = ?,
                    doctor_exit_code    = ?,
                    tests_passed        = ?,
                    tests_failed        = ?,
                    hallucination_flag  = ?,
                    regression_flag     = ?,
                    notes               = CASE WHEN ? != '' THEN ? ELSE notes END
                WHERE id = ?
                """,
                (
                    ended_at, duration_ms, completion_status,
                    tokens_input, tokens_output, cost_usd,
                    tool_calls_total, tool_calls_success, tool_calls_failed,
                    doctor_exit_code, tests_passed, tests_failed,
                    int(hallucination_flag), int(regression_flag),
                    notes, notes, run_id,
                ),
            )

    def record(self, **kwargs) -> str:
        """One-shot: start + immediately end a completed run."""
        run_id = self.start_run(
            task_name=kwargs.get("task_name", "unnamed"),
            stage=kwargs["stage"],
            agent=kwargs["agent"],
            task_tags=kwargs.get("task_tags"),
            notes=kwargs.get("notes", ""),
        )
        self.end_run(run_id, **{k: v for k, v in kwargs.items()
                                if k not in ("task_name", "stage", "agent",
                                             "task_tags", "notes")})
        return run_id

    def get_summary(self) -> list:
        """Return aggregated metrics across all runs."""
        with self._conn() as db:
            rows = db.execute("SELECT * FROM sdlc_metrics").fetchall()
        return [dict(row) for row in rows]

    def get_runs(self, limit: int = 100, stage: str | None = None) -> list:
        """Return recent runs, optionally filtered by stage."""
        with self._conn() as db:
            if stage:
                rows = db.execute(
                    "SELECT * FROM sdlc_runs WHERE stage = ? ORDER BY created_at DESC LIMIT ?",
                    (stage, limit),
                ).fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM sdlc_runs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(row) for row in rows]

    def get_kpis(self) -> dict:
        """Return top-level KPIs across all runs."""
        with self._conn() as db:
            row = db.execute("""
                SELECT
                    COUNT(*)                                                          AS total_runs,
                    SUM(CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END) AS completed,
                    ROUND(AVG(duration_ms) / 1000.0, 1)                              AS avg_duration_sec,
                    ROUND(SUM(cost_usd), 4)                                          AS total_cost_usd,
                    SUM(tool_calls_total)                                             AS tool_calls_total,
                    SUM(tool_calls_success)                                           AS tool_calls_success,
                    SUM(hallucination_flag)                                           AS hallucinations,
                    SUM(regression_flag)                                              AS regressions,
                    SUM(tests_passed)                                                 AS tests_passed,
                    SUM(tests_failed)                                                 AS tests_failed
                FROM sdlc_runs
            """).fetchone()
        kpis = dict(row)
        total = kpis.get("total_runs") or 1
        tool_total = kpis.get("tool_calls_total") or 1
        kpis["completion_rate_pct"] = round(100.0 * (kpis.get("completed") or 0) / total, 1)
        kpis["tool_success_rate_pct"] = round(
            100.0 * (kpis.get("tool_calls_success") or 0) / tool_total, 1
        )
        kpis["hallucination_rate_pct"] = round(
            100.0 * (kpis.get("hallucinations") or 0) / total, 1
        )
        return kpis

    # ── private ────────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        schema = _SCHEMA.read_text()
        with self._conn() as db:
            db.executescript(schema)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
