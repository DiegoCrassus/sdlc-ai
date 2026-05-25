"""Git branch and working-tree guards for SDLC hooks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

PROTECTED_BRANCHES = {"main", "master", "develop", "development"}
BRANCH_PATTERN = re.compile(r"^(feature|bugfix)/[A-Za-z]+-\d+$")


def _run_git(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def current_branch() -> str | None:
    return _run_git("rev-parse", "--abbrev-ref", "HEAD")


def is_protected_branch(branch: str | None = None) -> bool:
    name = branch or current_branch()
    if not name:
        return False
    return name in PROTECTED_BRANCHES


def branch_is_valid(branch: str | None = None) -> bool:
    name = branch or current_branch()
    if not name:
        return False
    return bool(BRANCH_PATTERN.match(name))


def has_uncommitted_changes() -> bool:
    status = _run_git("status", "--porcelain")
    return bool(status)


def uncommitted_summary(max_files: int = 8) -> str:
    status = _run_git("status", "--porcelain")
    if not status:
        return ""
    lines = status.splitlines()
    preview = "\n".join(lines[:max_files])
    if len(lines) > max_files:
        preview += f"\n… (+{len(lines) - max_files} arquivos)"
    return preview


def stop_context() -> str | None:
    branch = current_branch()
    if not branch:
        return None

    parts: list[str] = []

    if is_protected_branch(branch):
        parts.append(
            f"Branch atual `{branch}` é protegida. Antes de continuar, use o command "
            "`start_change` e a skill branch-naming para criar `feature/<RPG-N>` ou "
            "`bugfix/<RPG-N>` a partir de develop."
        )
    elif not branch_is_valid(branch):
        parts.append(
            f"Branch `{branch}` não segue o padrão SDLC "
            "`feature/<plane-task-id>` ou `bugfix/<plane-task-id>`. "
            "Renomeie ou recrie a branch antes do PR."
        )

    if has_uncommitted_changes():
        parts.append(
            "Há alterações não commitadas. Ao concluir a unidade de trabalho, "
            "use o command `finish_change` (validate → commit → push → PR)."
        )
        summary = uncommitted_summary()
        if summary:
            parts.append(f"Arquivos pendentes:\n{summary}")

    if not parts:
        return None
    return " ".join(parts)
