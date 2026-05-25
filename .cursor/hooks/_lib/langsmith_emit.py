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
    re.compile(r"LANGSMITH_API_KEY\s*=\s*\S+"),
]

CONTEXT_KEYS = (
    "conversation_id",
    "generation_id",
    "session_id",
    "hook_event_name",
    "cursor_version",
    "model",
    "tool_name",
    "tool_use_id",
    "mcp_tool",
    "mcp_server",
    "server",
)


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
    raw = _normalize_raw_json(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw[:2000]}


def _normalize_raw_json(raw: str) -> str:
    """Cursor hooks on Windows may deliver UTF-8 BOM as mojibake."""
    normalized = raw.lstrip("\ufeff").strip()
    if normalized.startswith("ï»¿"):
        normalized = normalized.removeprefix("ï»¿").strip()
    try:
        decoded = normalized.encode("latin-1").decode("utf-8-sig")
    except UnicodeError:
        return normalized
    return decoded.strip()


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
    load_env()
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


def _slug(value: Any, fallback: str = "unknown") -> str:
    text = str(value or fallback).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or fallback


def _git_branch() -> str | None:
    head = REPO_ROOT / ".git" / "HEAD"
    if not head.is_file():
        return None
    try:
        value = head.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if value.startswith("ref: refs/heads/"):
        return value.removeprefix("ref: refs/heads/")
    return value[:12] if value else None


def _extract_tool_input(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("tool_input", "input", "arguments"):
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _extract_context(data: dict[str, Any]) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for key in CONTEXT_KEYS:
        value = data.get(key)
        if value not in (None, "", [], {}):
            context[key] = sanitize(value, 300)

    tool_input = _extract_tool_input(data)
    if tool_input:
        cwd = tool_input.get("cwd") or data.get("cwd")
        if cwd:
            context["cwd"] = sanitize(str(cwd), 300)

    workspace_roots = data.get("workspace_roots")
    if isinstance(workspace_roots, list):
        context["workspace_roots"] = sanitize(workspace_roots, 300)

    branch = _git_branch()
    if branch:
        context["git_branch"] = branch
    context["repo_root"] = str(REPO_ROOT)
    return context


def _actor_key(data: dict[str, Any]) -> str:
    for key in ("subagent_id", "subagent_name", "agent_id", "agent_name", "agent", "subagent"):
        value = data.get(key)
        if value:
            return f"{key}:{value}"
    return str(data.get("conversation_id") or data.get("session_id") or "cursor")


def _session_context(event: str, raw_hook_input: dict[str, Any] | None) -> dict[str, Any]:
    session = get_session()
    data = raw_hook_input or {}
    now = datetime.now(timezone.utc).isoformat()

    if event == "sessionStart" or not session:
        session = {
            "session_id": str(data.get("session_id") or data.get("conversation_id") or uuid.uuid4()),
            "started_at": now,
            "project": _project(),
            "event_sequence": 0,
            "generation_map": {},
            "actor_map": {},
        }

    session["event_sequence"] = int(session.get("event_sequence") or 0) + 1

    generation_id = data.get("generation_id")
    generation_iteration = None
    if generation_id:
        generation_map = session.setdefault("generation_map", {})
        if generation_id not in generation_map:
            generation_map[generation_id] = len(generation_map) + 1
        generation_iteration = generation_map[generation_id]

    actor_map = session.setdefault("actor_map", {})
    actor_key = _actor_key(data)
    if actor_key not in actor_map:
        actor_map[actor_key] = len(actor_map) + 1
    actor_index = actor_map[actor_key]

    save_session(session)

    return {
        "session_id": session.get("session_id"),
        "event_sequence": session["event_sequence"],
        "generation_iteration": generation_iteration,
        "actor_index": actor_index,
        "actor_tag": f"cursor-subagent-{actor_index}",
    }


def _build_metadata(event: str, raw_hook_input: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw_hook_input or {}
    return {
        "event": event,
        "source": "cursor-hook",
        "sdlc_system": "rpg-op",
        "cursor": _extract_context(raw),
        "iteration": _session_context(event, raw),
    }


def _build_tags(event: str, metadata: dict[str, Any]) -> list[str]:
    cursor = metadata.get("cursor", {})
    iteration = metadata.get("iteration", {})
    tags = [
        "cursor",
        "cursor-hook",
        f"cursor-event-{_slug(event)}",
        str(iteration.get("actor_tag") or "cursor-subagent-1"),
    ]

    generation_iteration = iteration.get("generation_iteration")
    if generation_iteration:
        tags.append(f"cursor-iteration-{generation_iteration}")

    model = cursor.get("model")
    if model:
        tags.append(f"cursor-model-{_slug(model)}")

    tool = cursor.get("tool_name") or cursor.get("mcp_tool")
    if tool:
        tags.append(f"cursor-tool-{_slug(tool)}")

    branch = cursor.get("git_branch")
    if branch:
        tags.append(f"git-branch-{_slug(branch)}")

    return list(dict.fromkeys(tags))


def emit_run(
    event: str,
    inputs: dict[str, Any],
    *,
    outputs: dict[str, Any] | None = None,
    run_type: str = "chain",
    parent_run_id: str | None = None,
    raw_hook_input: dict[str, Any] | None = None,
) -> str | None:
    safe_inputs = sanitize(inputs)
    metadata = _build_metadata(event, raw_hook_input)
    tags = _build_tags(event, metadata)
    append_local(
        event,
        {
            "tags": tags,
            "metadata": sanitize(metadata),
            "inputs": safe_inputs,
            "outputs": sanitize(outputs or {}),
        },
    )

    client, project = _client()
    if client is None:
        return None

    try:
        run_id = str(uuid.uuid4())
        run_payload = {
            "id": run_id,
            "name": f"cursor/{event}",
            "run_type": run_type,
            "inputs": safe_inputs,
            "outputs": sanitize(outputs or {}) or None,
            "project_name": project,
            "parent_run_id": parent_run_id,
            "start_time": datetime.now(timezone.utc),
            "end_time": datetime.now(timezone.utc) if outputs is not None else None,
            "tags": tags,
            "extra": {"metadata": sanitize(metadata)},
        }
        try:
            client.create_run(**run_payload)
        except TypeError:
            run_payload.pop("extra", None)
            try:
                client.create_run(**run_payload)
            except TypeError:
                run_payload.pop("tags", None)
                client.create_run(**run_payload)
        return run_id
    except Exception as exc:
        print(json.dumps({"langsmith_error": str(exc)}), file=sys.stderr)
        return None


def emit_pre(
    event: str,
    hook_input: dict[str, Any],
    extra: dict[str, Any] | None = None,
    *,
    raw_hook_input: dict[str, Any] | None = None,
) -> None:
    session = get_session()
    payload = {"hook_input": hook_input, **(extra or {})}
    parent = session.get("root_run_id")
    run_id = emit_run(event, payload, parent_run_id=parent, raw_hook_input=raw_hook_input)
    if run_id and event == "sessionStart":
        session = get_session()
        session["root_run_id"] = run_id
        session["project"] = _project()
        session.setdefault("started_at", datetime.now(timezone.utc).isoformat())
        save_session(session)


def emit_post(
    event: str,
    hook_input: dict[str, Any],
    hook_output: dict[str, Any] | None = None,
    *,
    raw_hook_input: dict[str, Any] | None = None,
) -> None:
    session = get_session()
    payload = {"hook_input": hook_input, "hook_output": hook_output or {}}
    emit_run(
        event,
        payload,
        outputs={"status": "ok"},
        parent_run_id=session.get("root_run_id"),
        raw_hook_input=raw_hook_input,
    )


def respond(payload: dict[str, Any]) -> None:
    print(json.dumps(payload))
    sys.exit(0)


def path_targets_generated(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return normalized.startswith("generated/") or "/generated/" in normalized
