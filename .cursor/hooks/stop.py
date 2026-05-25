"""Post-hook: stop — log agent turn completion."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_post, read_stdin, respond


def main() -> None:
    data = read_stdin()
    emit_post("stop", data, raw_hook_input=data)
    respond({})


if __name__ == "__main__":
    main()
