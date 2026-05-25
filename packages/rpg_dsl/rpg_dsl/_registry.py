"""Global spec registry — populated by decorators at import time."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_registry: dict[str, list] = {
    "canvas": [],
    "sheet": [],
    "subagent": [],
    "eval": [],
    "api": [],
}


def register(kind: str, spec: object) -> None:
    if kind not in _registry:
        raise ValueError(f"Unknown spec kind: {kind!r}")
    _registry[kind].append(spec)


def get_all(kind: str) -> list:
    return list(_registry.get(kind, []))


def all_specs() -> dict[str, list]:
    return {k: list(v) for k, v in _registry.items()}


def clear() -> None:
    for k in _registry:
        _registry[k].clear()
