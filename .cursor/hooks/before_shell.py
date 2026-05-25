"""Pre-hook: beforeShellExecution — audit shell commands."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.git_guard import branch_is_valid, current_branch, is_protected_branch
from _lib.langsmith_emit import emit_pre, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    command = str(data.get("command") or "")
    emit_pre("beforeShellExecution", {"command": sanitize(command, 400)}, raw_hook_input=data)

    branch = current_branch()

    if "git push" in command and ("--force" in command or "-f " in command):
        if "main" in command or "master" in command:
            respond(
                {
                    "permission": "ask",
                    "user_message": "Force push para main/master requer confirmacao.",
                    "agent_message": "Hook SDLC flagged force push to default branch.",
                }
            )

    if branch and "git commit" in command and is_protected_branch(branch):
        respond(
            {
                "permission": "deny",
                "user_message": (
                    f"Commit bloqueado na branch protegida `{branch}`. "
                    "Use `start_change` e crie feature/RPG-N ou bugfix/RPG-N."
                ),
                "agent_message": (
                    "SDLC hook blocked commit on protected branch. "
                    "Run start_change with branch-naming skill first."
                ),
            }
        )

    if (
        branch
        and "git push" in command
        and not branch_is_valid(branch)
        and not is_protected_branch(branch)
    ):
        respond(
            {
                "permission": "ask",
                "user_message": (
                    f"Branch `{branch}` nao segue feature/RPG-N ou bugfix/RPG-N. "
                    "Renomeie antes do push ou confirme excecao."
                ),
                "agent_message": "SDLC branch naming validation failed before push.",
            }
        )

    respond({"permission": "allow"})


if __name__ == "__main__":
    main()
