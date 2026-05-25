"""Post-hook: sessionEnd — finalize LangSmith session."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import clear_session, emit_post, get_session, read_stdin, respond


def main() -> None:
    data = read_stdin()
    session = get_session()
    emit_post("sessionEnd", {**data, "session": session}, raw_hook_input=data)
    clear_session()
    respond({})


if __name__ == "__main__":
    main()
