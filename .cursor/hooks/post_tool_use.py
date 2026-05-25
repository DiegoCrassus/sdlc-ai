"""Post-hook: postToolUse — log successful tool execution."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_post, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    tool_name = str(data.get("tool_name") or data.get("name") or "unknown")
    emit_post(
        "postToolUse",
        {"tool": tool_name, "input": sanitize(data.get("tool_input") or data.get("input") or {})},
        {"result_preview": sanitize(data.get("result") or data.get("output") or {}, 800)},
        raw_hook_input=data,
    )
    respond({})


if __name__ == "__main__":
    main()
