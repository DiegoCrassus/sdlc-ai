"""Read-only pipeline and lifecycle metadata for Studio authoring UIs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from studio.compiler_core import CompilerInputError, compile_studio_sources
from studio_service.api.errors import StudioApiError


def build_pipeline_metadata(root: Path) -> dict[str, Any]:
    """Agents, skills, and lifecycle stages for dropdowns and asset palette."""

    lifecycle_path = root / ".sdlc" / "stages" / "lifecycle.yaml"
    pipeline_path = root / ".sdlc" / "pipeline" / "agents.yaml"

    stages = _load_lifecycle_stages(lifecycle_path)
    agents = _load_pipeline_agents(pipeline_path)

    skills: list[dict[str, str]] = []
    seen: set[str] = set()
    for agent in agents:
        skill = agent.get("skill") or {}
        skill_id = str(skill.get("id", ""))
        if skill_id and skill_id not in seen:
            seen.add(skill_id)
            skills.append({"id": skill_id, "name": str(skill.get("name", skill_id))})

    try:
        compiled = compile_studio_sources(root)
        workflow = (compiled.workflow_ir or {}).get("workflow") or {}
        transition_count = len(workflow.get("transitions") or [])
    except CompilerInputError as exc:
        raise StudioApiError(
            422,
            "COMPILER_INPUT_ERROR",
            "Required compiler inputs are missing or unreadable",
            details={"missing_paths": exc.missing_paths},
        ) from exc

    return {
        "stages": stages,
        "agents": agents,
        "skills": sorted(skills, key=lambda item: item["id"]),
        "summary": {
            "stage_count": len(stages),
            "agent_count": len(agents),
            "skill_count": len(skills),
            "transition_count": transition_count,
        },
        "source_refs": [
            ".sdlc/stages/lifecycle.yaml",
            ".sdlc/pipeline/agents.yaml",
            ".sdlc/workflows/transitions.yaml",
        ],
    }


def _load_lifecycle_stages(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    stages = []
    for item in data.get("stages") or []:
        if not isinstance(item, dict):
            continue
        stage_id = str(item.get("id", ""))
        stages.append(
            {
                "id": stage_id,
                "name": str(item.get("name", stage_id)),
                "order": item.get("order"),
                "description": str(item.get("description", "")),
            }
        )
    return sorted(stages, key=lambda s: (s.get("order") is None, s.get("order", 999), s["id"]))


def _load_pipeline_agents(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    agents = []
    for item in data.get("pipeline") or []:
        if not isinstance(item, dict):
            continue
        agent_id = str(item.get("id", ""))
        skill = item.get("skill") or {}
        agents.append(
            {
                "id": agent_id,
                "name": str(item.get("name", agent_id)),
                "stages": list(item.get("stages") or []),
                "cursor_agent": str(item.get("cursor_agent", "")),
                "skill": {
                    "id": str(skill.get("id", "")),
                    "name": str(skill.get("name", "")),
                },
            }
        )
    return agents
