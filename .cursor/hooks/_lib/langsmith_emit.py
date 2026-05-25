"""LangSmith + local audit for Cursor hooks."""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
LOG_DIR = REPO_ROOT / ".sdlc" / "logs"
SESSION_FILE = LOG_DIR / ".cursor-session.json"
JSONL_FILE = LOG_DIR / "cursor-hooks.jsonl"

SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"ghp_[a-zA-Z0-9]{20,}"),
    re.compile(r"GITHUB_PERSONAL_ACCESS_TOKEN\s*=\s*\S+"),
    re.compile(r"LANGCHAIN_API_KEY\s*=\s*\S+"),
]


def load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv(REPO_ROOT / ".env")
    except ImportError:
        pass


def read_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    raw = raw.lstrip("\ufeff").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw[:2000]}


def sanitize(value: Any, max_len: int = 500) -> Any:
    if isinstance(value, str):
        redacted = value
        for pattern in SECRET_PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        if len(redacted) > max_len:
            return redacted[:max_len] + "…"
        return redacted
    if isinstance(value, dict):
        return {k: sanitize(v, max_len) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v, max_len) for v in value[:20]]
    return value


def append_local(event: str, payload: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    with JSONL_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _project() -> str:
    # LangSmith SDK novo usa LANGSMITH_PROJECT; SDK antigo usa LANGCHAIN_PROJECT
    return os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or "rpg-op-cursor"


def _client():
    load_env()
    # Suporta tanto nomenclatura nova (LANGSMITH_*) quanto antiga (LANGCHAIN_*)
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    project = _project()
    if not api_key:
        return None, project
    try:
        from langsmith import Client

        return Client(api_key=api_key), project
    except Exception as exc:
        print(json.dumps({"langsmith_warning": str(exc)}), file=sys.stderr)
        return None, project


def get_session() -> dict[str, Any]:
    if SESSION_FILE.is_file():
        try:
            return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_session(data: dict[str, Any]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clear_session() -> None:
    if SESSION_FILE.is_file():
        SESSION_FILE.unlink()


def emit_run(
    event: str,
    inputs: dict[str, Any],
    *,
    outputs: dict[str, Any] | None = None,
    run_type: str = "chain",
    parent_run_id: str | None = None,
) -> str | None:
    safe_inputs = sanitize(inputs)
    append_local(event, {"inputs": safe_inputs, "outputs": sanitize(outputs or {})})

    client, project = _client()
    if client is None:
        return None

    try:
        run_id = str(uuid.uuid4())
        client.create_run(
            id=run_id,
            name=f"cursor/{event}",
            run_type=run_type,
            inputs=safe_inputs,
            outputs=sanitize(outputs or {}) or None,
            project_name=project,
            parent_run_id=parent_run_id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) if outputs is not None else None,
        )
        return run_id
    except Exception as exc:
        print(json.dumps({"langsmith_error": str(exc)}), file=sys.stderr)
        return None


def emit_pre(event: str, hook_input: dict[str, Any], extra: dict[str, Any] | None = None) -> None:
    session = get_session()
    payload = {"hook_input": hook_input, **(extra or {})}
    parent = session.get("root_run_id")
    run_id = emit_run(event, payload, parent_run_id=parent)
    if run_id and event == "sessionStart":
        save_session(
            {
                "session_id": str(uuid.uuid4()),
                "root_run_id": run_id,
                "project": _project(),
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )


def emit_post(
    event: str, hook_input: dict[str, Any], hook_output: dict[str, Any] | None = None
) -> None:
    session = get_session()
    payload = {"hook_input": hook_input, "hook_output": hook_output or {}}
    emit_run(
        event,
        payload,
        outputs={"status": "ok"},
        parent_run_id=session.get("root_run_id"),
    )


def respond(payload: dict[str, Any]) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def path_targets_generated(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return normalized.startswith("generated/") or "/generated/" in normalized
