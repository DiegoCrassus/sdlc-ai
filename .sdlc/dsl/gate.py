"""Session gate — mechanical write permissions for SDLC workflow."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


@dataclass
class SessionGate:
    gate_status: str = "closed"  # closed | open
    card: str = ""
    branch: str = ""
    stage: str = ""
    intent: str = ""
    opened_at: str = ""
    last_agent: str = ""       # last agent that updated the gate (e.g. "implementer")
    last_commit: str = ""      # last commit hash on the feature branch
    stage_started_at: str = "" # ISO timestamp when the current stage began
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionGate:
        return cls(
            gate_status=data.get("gate_status", "closed"),
            card=data.get("card", ""),
            branch=data.get("branch", ""),
            stage=data.get("stage", ""),
            intent=data.get("intent", ""),
            opened_at=data.get("opened_at", ""),
            last_agent=data.get("last_agent", ""),
            last_commit=data.get("last_commit", ""),
            stage_started_at=data.get("stage_started_at", ""),
            meta=data.get("meta") or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def repo_root(start: Path | None = None) -> Path:
    if start is None:
        start = Path(__file__).resolve()
    cur = start if start.is_dir() else start.parent
    for _ in range(8):
        if (cur / ".sdlc").is_dir() and (cur / "Makefile").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return Path(__file__).resolve().parents[2]


def gate_config_path(root: Path | None = None) -> Path:
    """Modular gate data (v5); legacy fallback to gate-paths.yaml."""
    base = (root or repo_root()) / ".sdlc"
    modular = base / "gates" / "paths.yaml"
    if modular.is_file():
        return modular
    return base / "gate-paths.yaml"


def session_gate_path(root: Path | None = None) -> Path:
    return (root or repo_root()) / ".sdlc" / "memory" / "session-gate.json"


def load_gate_config(root: Path | None = None) -> dict[str, Any]:
    path = gate_config_path(root)
    if yaml is None:
        raise RuntimeError("PyYAML required for gate config")
    if not path.is_file():
        raise FileNotFoundError(f"Missing gate config: {path}")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if path.name == "paths.yaml":
        return data.get("gate_paths") or {}
    return data.get("gate_paths") or data


def load_session_gate(root: Path | None = None) -> SessionGate:
    path = session_gate_path(root)
    if not path.is_file():
        return SessionGate()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return SessionGate()
    return SessionGate.from_dict(data)


def save_session_gate(state: SessionGate, root: Path | None = None) -> Path:
    path = session_gate_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def normalize_repo_path(file_path: str, root: Path | None = None) -> str:
    root = root or repo_root()
    p = Path(file_path)
    if p.is_absolute():
        try:
            rel = p.relative_to(root)
        except ValueError:
            return file_path.replace("\\", "/")
        return rel.as_posix()
    return file_path.replace("\\", "/").lstrip("./")


def _matches_prefix(rel_path: str, prefix: str) -> bool:
    if prefix.endswith("/"):
        return rel_path.startswith(prefix) or rel_path == prefix.rstrip("/")
    return rel_path == prefix or rel_path.startswith(prefix + "/")


def is_protected(rel_path: str, config: dict[str, Any]) -> bool:
    for prefix in config.get("protected_prefixes", []):
        if _matches_prefix(rel_path, prefix):
            return True
    return False


def stage_allows(rel_path: str, stage: str, config: dict[str, Any]) -> bool:
    stages = config.get("stages") or {}
    stage_cfg = stages.get(stage) or {}
    allowed = stage_cfg.get("allowed_prefixes") or []
    return any(_matches_prefix(rel_path, p) for p in allowed)


def check_write(rel_path: str, root: Path | None = None) -> tuple[bool, str]:
    root = root or repo_root()
    rel = normalize_repo_path(rel_path, root)
    config = load_gate_config(root)
    state = load_session_gate(root)

    if not is_protected(rel, config):
        return True, "path not protected"

    if state.gate_status != "open":
        return False, (
            f"Gate closed — cannot write to protected path '{rel}'. "
            f"Run: python3 .sdlc/dsl/cli.py workflow start --card INVES-N --stage <stage>"
        )

    if not state.stage:
        return False, "Gate open but stage unset — run workflow start with --stage"

    if stage_allows(rel, state.stage, config):
        return True, f"allowed for stage '{state.stage}'"

    return False, (
        f"Path '{rel}' not allowed for stage '{state.stage}'. "
        f"Advance stage or use workflow start with correct --stage."
    )


def open_gate(
    *,
    card: str,
    branch: str,
    stage: str,
    intent: str = "",
    last_agent: str = "",
    last_commit: str = "",
    root: Path | None = None,
) -> SessionGate:
    now = datetime.now(UTC).isoformat()
    state = SessionGate(
        gate_status="open",
        card=card,
        branch=branch,
        stage=stage,
        intent=intent,
        opened_at=now,
        last_agent=last_agent,
        last_commit=last_commit,
        stage_started_at=now,
    )
    save_session_gate(state, root)
    return state


def close_gate(root: Path | None = None) -> SessionGate:
    state = SessionGate(gate_status="closed")
    save_session_gate(state, root)
    return state


def gate_status_text(root: Path | None = None) -> str:
    state = load_session_gate(root)
    lines = [
        f"gate_status: {state.gate_status}",
        f"card: {state.card or '(none)'}",
        f"branch: {state.branch or '(none)'}",
        f"stage: {state.stage or '(none)'}",
        f"intent: {state.intent or '(none)'}",
        f"opened_at: {state.opened_at or '(none)'}",
        f"last_agent: {state.last_agent or '(none)'}",
        f"last_commit: {state.last_commit or '(none)'}",
        f"stage_started_at: {state.stage_started_at or '(none)'}",
    ]
    return "\n".join(lines)
