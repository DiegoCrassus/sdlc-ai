#!/usr/bin/env python3
"""Cursor preToolUse — block Write when SDLC gate is closed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DSL = REPO / ".sdlc" / "dsl"

if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

try:
    import gate as _gate  # noqa: E402
except Exception as _gate_exc:
    _GATE_LOAD_FAILED = _gate_exc
else:
    _GATE_LOAD_FAILED = None


def _deny(user: str, agent: str) -> None:
    print(json.dumps({"permission": "deny", "user_message": user, "agent_message": agent}))
    sys.exit(0)


def _extract_write_path(payload: dict) -> str:
    tool_input = payload.get("tool_input") or payload.get("input") or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except json.JSONDecodeError:
            return ""
    for key in ("path", "file_path", "target_file"):
        if val := tool_input.get(key):
            return str(val)
    return ""


def _emit_gate_event(event_type: str, payload: dict) -> None:
    try:
        hooks_dir = Path(__file__).resolve().parent
        if str(hooks_dir) not in sys.path:
            sys.path.insert(0, str(hooks_dir))
        from sdlc_gateway_lib import emit_studio_event  # noqa: PLC0415

        emit_studio_event(event_type, "sdlc_gate_hook", payload, category="gate")
    except Exception:
        return


def main() -> None:
    if _GATE_LOAD_FAILED is not None:
        _deny(
            "SDLC gate module failed to load — write blocked.",
            f"Fix .sdlc/dsl/gate.py import error: {_GATE_LOAD_FAILED}",
        )

    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        _deny("SDLC gate: invalid payload.", "Non-JSON stdin on Write hook.")

    rel = _extract_write_path(payload)
    if not rel:
        print(json.dumps({"permission": "allow"}))
        return

    ok, msg = _gate.check_write(rel, REPO)
    if ok:
        _emit_gate_event("gate.write_allowed", {"path": rel, "tool": "Write"})
        print(json.dumps({"permission": "allow"}))
        return

    card = _gate.load_session_gate(REPO).card or "INVES-N"
    _emit_gate_event(
        "gate.write_denied",
        {"path": rel, "reason": msg, "card_required": card},
    )
    _deny(
        "SDLC gate: write blocked on protected path.",
        f"Blocked '{rel}'. {msg} Run: workflow start --card {card} --stage sdlc_meta",
    )


if __name__ == "__main__":
    main()
