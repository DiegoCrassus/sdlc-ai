"""Load vendor-neutral core section from .sdlc/sdlc.yaml."""

from __future__ import annotations

import re
from pathlib import Path
from re import Pattern
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _sdlc_path(root: Path) -> Path:
    return root / ".sdlc" / "sdlc.yaml"


def load_core(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    path = _sdlc_path(root)
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("core") or {}


def workboard(root: str | Path) -> dict[str, Any]:
    return (load_core(root).get("vendors") or {}).get("workboard") or {}


def env_map(root: str | Path) -> dict[str, str]:
    """Logical env name -> OS variable name."""
    return load_core(root).get("env") or {}


def card_pattern(root: str | Path) -> Pattern[str]:
    wb = workboard(root)
    prefix = str(wb.get("card_prefix") or "INVES")
    return re.compile(rf"^{re.escape(prefix)}-(\d+)$", re.IGNORECASE)


def skill_path(root: str | Path, rel: str) -> Path:
    """Resolve skill path from catalog relative path."""
    root = Path(root)
    return root / rel
