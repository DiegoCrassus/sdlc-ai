"""Tests for DPA template analyzer."""

from app.services.dpa_analyzer import analyze_template


def test_analyze_file_source_returns_steps():
    result = analyze_template(sheet_source="file", sheet_input_raw=None, has_image=True)
    assert len(result.steps) >= 2
    assert result.sheet_schema.get("fields")
    assert result.canvas_spec.get("regions")
    assert result.confidence in {"low", "medium", "high"}


def test_analyze_text_source():
    result = analyze_template(
        sheet_source="text",
        sheet_input_raw="Ficha com nome, classe, seis atributos e anotações.",
        has_image=False,
    )
    assert result.warnings
    assert "character_name" in result.sheet_schema["fields"]
