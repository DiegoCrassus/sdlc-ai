"""Unified Studio observability event store (SQLite)."""

from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_DEFAULT_DB = Path(__file__).parent / "data" / "sdlc_obs.db"
_SCHEMA = Path(__file__).parent / "schema.sql"

SCHEMA_VERSION = "1.0"
VALID_CATEGORIES = frozenset({"gateway", "obs", "handoff", "gate"})

_CARD_RE = re.compile(r"INVES-\d+", re.IGNORECASE)


def category_for_event_type(event_type: str) -> str:
    if event_type.startswith("gateway."):
        return "gateway"
    if event_type.startswith("obs."):
        return "obs"
    if event_type.startswith("handoff."):
        return "handoff"
    if event_type.startswith("gate.") or event_type.startswith("session.gate"):
        return "gate"
    return "gateway"


def extract_card(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        match = _CARD_RE.search(value)
        if match:
            return match.group(0).upper()
    return None


def build_correlation_id(correlation: dict[str, Any]) -> str:
    parts: list[str] = []
    if run_id := correlation.get("run_id"):
        parts.append(f"run:{run_id}")
    if card := correlation.get("card"):
        parts.append(f"card:{card}")
    if branch := correlation.get("branch"):
        parts.append(f"branch:{branch}")
    return "|".join(parts)


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class EventStore:
    """Append-only store for unified timeline events."""

    def __init__(self, db_path: Path | None = None) -> None:
        if db_path is not None:
            resolved = Path(db_path)
        elif env_db := os.environ.get("SDLC_OBS_DB"):
            resolved = Path(env_db)
        else:
            resolved = _DEFAULT_DB
        self.db_path = resolved
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def append_event(
        self,
        *,
        event_type: str,
        source: str,
        payload: dict[str, Any] | None = None,
        correlation: dict[str, Any] | None = None,
        category: str | None = None,
        timestamp: str | None = None,
        event_id: str | None = None,
    ) -> dict[str, Any]:
        resolved_category = category or category_for_event_type(event_type)
        if resolved_category not in VALID_CATEGORIES:
            raise ValueError(f"Unknown category: {resolved_category!r}")

        corr = dict(correlation or {})
        if card := extract_card(corr.get("card"), corr.get("branch"), (payload or {}).get("task_name")):
            corr.setdefault("card", card)

        event = {
            "schema_version": SCHEMA_VERSION,
            "event_id": event_id or f"evt_{uuid.uuid4()}",
            "event_type": event_type,
            "category": resolved_category,
            "timestamp": timestamp or utc_now_iso(),
            "source": source,
            "correlation_id": build_correlation_id(corr),
            "correlation": corr,
            "payload": payload or {},
        }

        with self._conn() as db:
            db.execute(
                """
                INSERT INTO sdlc_events
                    (id, category, event_type, source, timestamp,
                     schema_version, correlation_id, correlation, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["event_id"],
                    event["category"],
                    event["event_type"],
                    event["source"],
                    event["timestamp"],
                    event["schema_version"],
                    event["correlation_id"],
                    json.dumps(event["correlation"]),
                    json.dumps(event["payload"]),
                ),
            )
        return event

    def list_events(
        self,
        *,
        limit: int = 100,
        since: str | None = None,
        category: str | None = None,
        card: str | None = None,
        run_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []

        if since:
            clauses.append("timestamp >= ?")
            params.append(since)
        if category:
            clauses.append("category = ?")
            params.append(category)
        if card:
            clauses.append("(correlation LIKE ? OR correlation_id LIKE ?)")
            needle = f"%{card.upper()}%"
            params.extend([needle, needle])
        if run_id:
            clauses.append("(correlation LIKE ? OR correlation_id LIKE ?)")
            needle = f"%{run_id}%"
            params.extend([needle, needle])
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT id, category, event_type, source, timestamp, schema_version,
                   correlation_id, correlation, payload
            FROM sdlc_events
            {where}
            ORDER BY timestamp ASC, id ASC
            LIMIT ?
        """
        params.append(limit)

        with self._conn() as db:
            rows = db.execute(sql, params).fetchall()
        return [self._row_to_event(row) for row in rows]

    def runs_as_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._conn() as db:
            rows = db.execute(
                """
                SELECT id, task_name, stage, agent, started_at, ended_at,
                       duration_ms, completion_status, doctor_exit_code,
                       tests_passed, tests_failed, hallucination_flag
                FROM sdlc_runs
                ORDER BY started_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        events: list[dict[str, Any]] = []
        for row in rows:
            run = dict(row)
            correlation = {
                "run_id": run["id"],
                "card": extract_card(run["task_name"]),
            }
            started_ts = datetime.fromtimestamp(run["started_at"], UTC).replace(microsecond=0)
            started_iso = started_ts.isoformat().replace("+00:00", "Z")
            events.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "event_id": f"evt_run_start_{run['id']}",
                    "event_type": "obs.run_started",
                    "category": "obs",
                    "timestamp": started_iso,
                    "source": "sdlc_obs",
                    "correlation_id": build_correlation_id(correlation),
                    "correlation": correlation,
                    "payload": {
                        "task_name": run["task_name"],
                        "stage": run["stage"],
                        "agent": run["agent"],
                    },
                }
            )
            if run["ended_at"]:
                ended_ts = datetime.fromtimestamp(run["ended_at"], UTC).replace(microsecond=0)
                ended_iso = ended_ts.isoformat().replace("+00:00", "Z")
                events.append(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "event_id": f"evt_run_end_{run['id']}",
                        "event_type": "obs.run_ended",
                        "category": "obs",
                        "timestamp": ended_iso,
                        "source": "sdlc_obs",
                        "correlation_id": build_correlation_id(correlation),
                        "correlation": correlation,
                        "payload": {
                            "completion_status": run["completion_status"],
                            "duration_ms": run["duration_ms"],
                            "doctor_exit_code": run["doctor_exit_code"],
                            "tests_passed": run["tests_passed"],
                            "tests_failed": run["tests_failed"],
                            "hallucination_flag": bool(run["hallucination_flag"]),
                        },
                    }
                )
        return events

    def build_timeline(
        self,
        *,
        limit: int = 100,
        since: str | None = None,
        category: str | None = None,
        card: str | None = None,
        run_id: str | None = None,
        event_type: str | None = None,
        include_runs: bool = True,
    ) -> list[dict[str, Any]]:
        stored = self.list_events(
            limit=limit * 2,
            since=since,
            category=category if category and category != "obs" else None,
            card=card,
            run_id=run_id,
            event_type=event_type,
        )
        events = list(stored)
        if include_runs and (category is None or category == "obs"):
            run_events = self.runs_as_events(limit=limit * 2)
            if since:
                run_events = [e for e in run_events if e["timestamp"] >= since]
            if card:
                needle = card.upper()
                run_events = [
                    e
                    for e in run_events
                    if needle in (e.get("correlation") or {}).get("card", "")
                    or needle in e.get("correlation_id", "")
                ]
            if run_id:
                run_events = [
                    e
                    for e in run_events
                    if run_id in (e.get("correlation") or {}).get("run_id", "")
                    or run_id in e.get("correlation_id", "")
                ]
            if event_type:
                run_events = [e for e in run_events if e["event_type"] == event_type]
            events.extend(run_events)

        events.sort(key=lambda item: (item["timestamp"], item["event_id"]))
        if category:
            events = [e for e in events if e["category"] == category]
        return events[-limit:]

    def _row_to_event(self, row: sqlite3.Row) -> dict[str, Any]:
        correlation = json.loads(row["correlation"] or "{}")
        payload = json.loads(row["payload"] or "{}")
        return {
            "schema_version": row["schema_version"],
            "event_id": row["id"],
            "event_type": row["event_type"],
            "category": row["category"],
            "timestamp": row["timestamp"],
            "source": row["source"],
            "correlation_id": row["correlation_id"],
            "correlation": correlation,
            "payload": payload,
        }

    def _init_db(self) -> None:
        schema = _SCHEMA.read_text(encoding="utf-8")
        with self._conn() as db:
            db.executescript(schema)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
