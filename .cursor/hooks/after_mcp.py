"""Post-hook: afterMCPExecution — log MCP results."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_post, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    tool = str(data.get("tool_name") or data.get("name") or "mcp")
    emit_post(
        "afterMCPExecution",
        {"tool": tool, "server": str(data.get("server") or "")},
        {"result_preview": sanitize(data.get("result") or data.get("output") or {}, 800)},
        raw_hook_input=data,
    )
    respond({})


if __name__ == "__main__":
    main()
