"""IR for sheet-template-analyst / DPA Agent output."""

from typing import Literal

from pydantic import BaseModel, Field


class AnalysisStep(BaseModel):
    id: str
    label: str
    finding: str
    fields: list[dict] = Field(default_factory=list)


class SheetSchemaDraft(BaseModel):
    version: int = 1
    fields: dict[str, dict] = Field(default_factory=dict)


class CanvasSpecDraft(BaseModel):
    version: int = 1
    layout: str = "regions"
    regions: list[dict] = Field(default_factory=list)
    styling: dict = Field(default_factory=lambda: {"density": "compact", "show_labels": True})
    role_overrides: dict = Field(
        default_factory=lambda: {
            "player": {"readonly_fields": []},
            "gm": {"readonly_fields": []},
        }
    )


class TemplateAnalysisResult(BaseModel):
    """Structured output from DPA Agent template analysis."""

    steps: list[AnalysisStep]
    sheet_schema: SheetSchemaDraft
    canvas_spec: CanvasSpecDraft
    warnings: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"

    model_config = {"extra": "forbid"}
