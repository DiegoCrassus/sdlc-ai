"""Post-hook: afterShellExecution — log shell output."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_post, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    emit_post(
        "afterShellExecution",
        {"command": sanitize(str(data.get("command") or ""), 400)},
        {"output_preview": sanitize(str(data.get("output") or data.get("stdout") or ""), 800)},
    )
    respond({})


if __name__ == "__main__":
    main()
