"""Product orchestrator manifest for the MVP agent boundary."""

from typing import ClassVar

from rpg_dsl import SubAgent


@SubAgent(name="orchestrator", response_model="OrchestratorResult")
class ProductOrchestrator:
    skills: ClassVar[list[str]] = [
        "workflows/sheet-canvas/",
        "workflows/template-publish/",
    ]
