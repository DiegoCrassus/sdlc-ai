"""Plane task granularity validation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

AI_TYPE_RE = re.compile(r"\[AI\]\[([A-Z]+)\]", re.IGNORECASE)
INVES_RE = re.compile(r"INVES-(\d+)", re.IGNORECASE)


def load_granularity_config(root: Path) -> dict[str, Any]:
    modular = root / ".sdlc" / "workboard" / "granularity.yaml"
    legacy = root / ".sdlc" / "plane-granularity.yaml"
    path = modular if modular.is_file() else legacy
    if yaml is None or not path.is_file():
        return {}
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("workboard_granularity") or data.get("plane_granularity") or data


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def detect_intent_from_handoff(root: Path) -> str:
    handoff = root / ".sdlc" / "memory" / "orchestrator-handoff.md"
    if not handoff.is_file():
        return "FEATURE"
    content = handoff.read_text(encoding="utf-8").lower()
    for key in ("greenfield", "feature", "bugfix", "hotfix", "sdlc_meta", "docs_only", "infra"):
        if f"intent: {key}" in content or f"intent:{key}" in content:
            return key.upper()
    return "FEATURE"


def extract_ai_types(text: str) -> set[str]:
    return {m.upper() for m in AI_TYPE_RE.findall(text)}


def validate_granularity(
    issue: dict[str, Any],
    *,
    intent: str,
    child_count: int = 0,
    config: dict[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    """Return list of failure messages; empty = pass."""
    root = root or Path(__file__).resolve().parents[2]
    config = config or load_granularity_config(root)
    failures: list[str] = []

    name = (issue.get("name") or "").strip()
    html = issue.get("description_html") or ""
    text = strip_html(html)
    combined = f"{name} {text}"
    name_upper = name.upper()
    intent = intent.upper()

    requires_epic = intent in set(config.get("requires_epic") or [])
    single_ok = intent in set(config.get("single_card_allowed") or [])

    if single_ok:
        return failures

    forbidden = [t.upper() for t in config.get("forbidden_sole_tags") or []]
    for tag in forbidden:
        if tag in name_upper and child_count == 0:
            failures.append(
                f"FORBIDDEN sole card tag {tag} for intent {intent} — create [AI][EPIC] + child cards"
            )

    epic_tag = (config.get("epic_tag") or "[AI][EPIC]").upper()
    is_epic = epic_tag in name_upper

    if requires_epic and not is_epic and child_count == 0:
        # Might be a child card — allowed if title has specific TYPE not FULLSTACK
        if any(tag in name_upper for tag in forbidden):
            failures.append("Child/implementable card cannot be FULLSTACK — use BACKEND, FRONTEND, etc.")
        return failures

    if not is_epic:
        return failures

    min_layers = (config.get("min_impl_layers") or {}).get(intent, 2)
    impl_types = extract_ai_types(text) - {"EPIC", "PLAN", "FULLSTACK"}
    layer_types = impl_types & {"BACKEND", "FRONTEND", "INFRA", "SHARED", "DOCS", "SDLC"}
    if len(layer_types) < min_layers:
        failures.append(
            f"Epic Task Breakdown needs >={min_layers} distinct [AI][TYPE] layers; found: {sorted(layer_types)}"
        )

    min_children = (config.get("min_child_cards") or {}).get(intent, 2)
    breakdown_refs = set(INVES_RE.findall(combined))
    effective_children = max(child_count, len(breakdown_refs))
    if effective_children < min_children:
        failures.append(
            f"Epic needs >={min_children} child cards (Plane parent links or INVES-N in breakdown); "
            f"found {effective_children}"
        )

    if intent == "GREENFIELD":
        groups = config.get("greenfield_required_groups") or []
        for group in groups:
            tags = [t.upper() for t in group.get("tags") or []]
            label = group.get("label", "group")
            min_match = group.get("min_match", 1)
            matches = sum(1 for t in tags if t in name_upper or t in combined.upper())
            if matches < min_match:
                failures.append(f"GREENFIELD epic missing breakdown for: {label} ({tags})")

    breakdown_markers = ("task breakdown", "sub-tasks", "sub tasks", "child cards", "cards filhos")
    if not any(m in text.lower() for m in breakdown_markers):
        failures.append("Epic must include Task Breakdown / child cards section")

    return failures
