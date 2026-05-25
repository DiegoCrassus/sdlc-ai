"""Detect generated GitHub issues and point the workflow to issue-resolver."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import append_local, read_stdin, respond, sanitize

ISSUE_PATTERNS = [
    re.compile(r"Created issue #(?P<number>\d+)", re.IGNORECASE),
    re.compile(r"github\.com/[^/\s]+/[^/\s]+/issues/(?P<number>\d+)", re.IGNORECASE),
    re.compile(r"\[lint-fail\]", re.IGNORECASE),
    re.compile(r"sdlc:blocked", re.IGNORECASE),
]


def _payload_text(data: dict) -> str:
    parts = [
        str(data.get("tool_name") or data.get("name") or ""),
        str(data.get("command") or ""),
        str(data.get("result") or data.get("output") or ""),
        str(data.get("tool_input") or data.get("input") or ""),
    ]
    return "\n".join(parts)


def main() -> None:
    data = read_stdin()
    text = _payload_text(data)
    matches = [pattern.search(text) for pattern in ISSUE_PATTERNS]
    if not any(matches):
        respond({})

    issue_number = next((m.groupdict().get("number") for m in matches if m and m.groupdict()), None)
    payload = {
        "issue_number": issue_number,
        "source": str(data.get("tool_name") or data.get("name") or data.get("event") or "unknown"),
        "preview": sanitize(text, 1000),
        "next_agent": "issue-resolver",
        "command": "issue_resolution",
    }
    append_local("issueGenerated", payload)
    respond(
        {
            "additional_context": (
                "Uma issue GitHub parece ter sido gerada. Use o command `issue_resolution` "
                "e delegue ao subagente `issue-resolver`; mova o card Plane relacionado "
                "para In Progress e registre evidências antes de fechar."
            )
        }
    )


if __name__ == "__main__":
    main()
