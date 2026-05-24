"""Pre-hook: beforeMCPExecution — audit MCP (GitHub) calls."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_pre, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    tool = str(data.get("tool_name") or data.get("name") or data.get("mcp_tool") or "mcp")
    server = str(data.get("server") or data.get("mcp_server") or "")
    emit_pre(
        "beforeMCPExecution",
        {
            "tool": tool,
            "server": server,
            "input": sanitize(data.get("tool_input") or data.get("arguments") or {}),
        },
    )
    respond({"permission": "allow"})


if __name__ == "__main__":
    main()
