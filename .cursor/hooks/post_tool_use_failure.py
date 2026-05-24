"""Post-hook: postToolUseFailure — log failed tools."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_post, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    emit_post(
        "postToolUseFailure",
        sanitize(data),
        {"status": "error", "error": sanitize(str(data.get("error") or ""), 500)},
    )
    respond({})


if __name__ == "__main__":
    main()
