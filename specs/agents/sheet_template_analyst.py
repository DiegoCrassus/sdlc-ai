"""sheet-template-analyst — MVP subagente que analisa PDFs/imagens de fichas."""

from typing import ClassVar

from rpg_dsl import SubAgent


@SubAgent(name="sheet-template-analyst", response_model="TemplateAnalysisResult")
class SheetTemplateAnalyst:
    skills: ClassVar[list[str]] = [
        "workflows/template-analysis/",
    ]
