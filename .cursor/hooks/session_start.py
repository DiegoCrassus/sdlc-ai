"""Pre-hook: sessionStart — init LangSmith root run + SDLC context."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import clear_session, emit_pre, read_stdin, respond

SESSION_CONTEXT = (
    "SDLC RPG-OP: siga .sdlc/AGENTS.md, .sdlc/phases.yaml e change-lifecycle. "
    "Antes de codar: command start_change + branch feature/RPG-N ou bugfix/RPG-N. "
    "Ao concluir: finish_change (validate, commit, push, PR). "
    "Nao edite generated/ manualmente. Logs desta sessao vao para LangSmith (projeto LANGCHAIN_PROJECT)."
)


def main() -> None:
    data = read_stdin()
    clear_session()
    emit_pre("sessionStart", data, extra={"project": "rpg-op-cursor"}, raw_hook_input=data)
    respond({"continue": True, "additional_context": SESSION_CONTEXT})


if __name__ == "__main__":
    main()
