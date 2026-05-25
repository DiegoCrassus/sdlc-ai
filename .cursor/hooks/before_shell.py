"""Pre-hook: beforeShellExecution — audit shell commands."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import emit_pre, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    command = str(data.get("command") or "")
    emit_pre("beforeShellExecution", {"command": sanitize(command, 400)}, raw_hook_input=data)

    if "git push" in command and ("--force" in command or "-f " in command):
        if "main" in command or "master" in command:
            respond(
                {
                    "permission": "ask",
                    "user_message": "Force push para main/master requer confirmacao.",
                    "agent_message": "Hook SDLC flagged force push to default branch.",
                }
            )

    respond({"permission": "allow"})


if __name__ == "__main__":
    main()
