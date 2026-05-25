"""Tests for MVP4 template extension."""

import pytest

from app.fixtures.default_template import DEFAULT_CANVAS_SPEC, DEFAULT_SCHEMA
from app.services.template_extend import (
    TemplateExtendError,
    extend_from_description,
    extend_template,
    field_has_data,
    merge_new_fields_into_sheet,
    remove_field,
)


def test_extend_appends_field_append_only():
    schema, canvas, patch = extend_template(
        DEFAULT_SCHEMA,
        DEFAULT_CANVAS_SPEC,
        field_key="mount",
        field_label="Montaria",
        field_type="string",
        region_id="extensions",
        region_title="Extensões",
        create_region=True,
    )
    assert "mount" in schema["fields"]
    assert patch["action"] == "append_field"
    region = next(r for r in canvas["regions"] if r["id"] == "extensions")
    assert "mount" in region["fields"]


def test_extend_rejects_duplicate_field():
    with pytest.raises(TemplateExtendError):
        extend_template(
            DEFAULT_SCHEMA,
            DEFAULT_CANVAS_SPEC,
            field_key="character_name",
            field_label="Nome",
        )


def test_extend_from_description_parses_campo():
    schema, canvas, patch = extend_from_description(
        DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC, "campo Montaria string"
    )
    assert patch["field_key"] == "montaria"
    assert "montaria" in schema["fields"]


def test_merge_new_fields_preserves_existing_data():
    previous = set(DEFAULT_SCHEMA["fields"].keys())
    data = {"character_name": "Lyra", "level": 3}
    merged = merge_new_fields_into_sheet(data, DEFAULT_SCHEMA, previous)
    assert merged["character_name"] == "Lyra"
    assert merged["level"] == 3

    extended_schema, _, _ = extend_template(
        DEFAULT_SCHEMA,
        DEFAULT_CANVAS_SPEC,
        field_key="mount",
        field_label="Montaria",
    )
    merged2 = merge_new_fields_into_sheet(data, extended_schema, previous)
    assert merged2["character_name"] == "Lyra"
    assert merged2["mount"] == ""


def test_remove_field_requires_confirm_when_data_exists():
    schema = {
        "fields": {
            "name": {"type": "string", "label": "Nome"},
            "mount": {"type": "string", "label": "Montaria"},
        }
    }
    canvas = {
        "regions": [{"id": "main", "fields": ["name", "mount"]}],
    }
    sheets = [{"name": "A", "mount": "Cavalo"}]

    with pytest.raises(TemplateExtendError) as exc:
        remove_field(schema, canvas, "mount", sheets, confirm=False)
    assert exc.value.needs_confirm

    new_schema, new_canvas, patch = remove_field(schema, canvas, "mount", sheets, confirm=True)
    assert "mount" not in new_schema["fields"]
    assert patch["affected_sheets"] == 1


def test_field_has_data():
    assert field_has_data({"notes": "abc"}, "notes")
    assert not field_has_data({"notes": ""}, "notes")
    assert not field_has_data({}, "notes")
