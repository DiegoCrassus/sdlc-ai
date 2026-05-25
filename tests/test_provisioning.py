"""Tests for workspace sheet provisioning."""

import pytest
from fastapi import HTTPException

from app.services.provisioning import provision_from_json, provision_from_text


def test_provision_from_json_with_schema_and_canvas():
    raw = """
    {
      "schema": {"version": 1, "fields": {"name": {"type": "string", "label": "Nome"}}},
      "canvas_spec": {
        "version": 1,
        "layout": "regions",
        "regions": [{"id": "main", "title": "X", "order": 0, "presentation": "field_grid", "fields": ["name"]}]
      },
      "data": {"name": "Test"}
    }
    """
    schema, canvas, data = provision_from_json(raw)
    assert schema["fields"]["name"]["label"] == "Nome"
    assert canvas["regions"][0]["fields"] == ["name"]
    assert data["name"] == "Test"


def test_provision_from_json_fields_only_generates_canvas():
    raw = '{"version": 1, "fields": {"hp": {"type": "integer", "label": "PV", "min": 0}}}'
    schema, canvas, data = provision_from_json(raw)
    assert "hp" in schema["fields"]
    assert canvas["regions"]
    assert data["hp"] == 0


def test_provision_from_text_requires_min_length():
    with pytest.raises(HTTPException):
        provision_from_text("curto")


def test_provision_from_text_uses_default_template():
    schema, canvas, data = provision_from_text("Ficha com nome, classe, atributos e anotações livres.")
    assert "character_name" in schema["fields"]
    assert canvas["regions"]
    assert data["character_name"]
