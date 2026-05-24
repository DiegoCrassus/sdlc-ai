"""Pre-hook: preToolUse — block writes to generated/, audit tool call."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_pre, path_targets_generated, read_stdin, respond, sanitize


def _tool_path(data: dict) -> str:
    tool_input = data.get("tool_input") or data.get("input") or {}
    if isinstance(tool_input, dict):
        for key in ("path", "file_path", "target_file", "filePath"):
            if tool_input.get(key):
                return str(tool_input[key])
    return ""


def main() -> None:
    data = read_stdin()
    tool_name = str(data.get("tool_name") or data.get("name") or "unknown")
    emit_pre("preToolUse", {"tool": tool_name, "input": sanitize(data)})

    if tool_name in {"Write", "Edit", "edit_file", "write_file"}:
        target = _tool_path(data)
        if target and path_targets_generated(target):
            respond(
                {
                    "permission": "deny",
                    "user_message": "Arquivos em generated/ sao somente leitura. Rode rpg compile.",
                    "agent_message": "Use specs/ + rpg compile instead of editing generated/.",
                }
            )

    respond({"permission": "allow"})


if __name__ == "__main__":
    main()
