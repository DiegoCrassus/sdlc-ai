#!/usr/bin/env python3
"""
Cursor preToolUse hook — block Write to protected paths when SDLC gate is closed.

Hook event: preToolUse (matcher: Write)
Exit 0 + permission deny JSON = block write
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DSL = REPO / ".sdlc" / "dsl"

if str(DSL) not in sys.path:
    sys.path.insert(0, str(DSL))

import importlib.util

_spec = importlib.util.spec_from_file_location("_gate", DSL / "gate.py")
if _spec is None or _spec.loader is None:
    print(json.dumps({"permission": "allow"}))
    sys.exit(0)

_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gate)


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
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    rel_path = _extract_write_path(payload)
    if not rel_path:
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    ok, msg = _gate.check_write(rel_path, REPO)
    if ok:
        _emit_gate_event("gate.write_allowed", {"path": rel_path, "tool": "Write"})
        print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    card = _gate.load_session_gate(REPO).card or "INVES-N"
    _emit_gate_event(
        "gate.write_denied",
        {
            "path": rel_path,
            "reason": msg,
            "card_required": card,
        },
    )
    agent_msg = (
        f"SDLC gate blocked write to '{rel_path}'. {msg} "
        f"Auto-fix: python3 .sdlc/dsl/cli.py workflow start --card {card} --stage sdlc_meta "
        f"(product impl: --stage implementation)"
    )
    print(
        json.dumps(
            {
                "permission": "deny",
                "user_message": "SDLC gate: write blocked on protected path.",
                "agent_message": agent_msg,
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
