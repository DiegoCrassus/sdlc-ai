"""Tests for sheet validation and permissions."""

import pytest

from app.services.sheet_permissions import field_permissions, readonly_fields_for_role
from app.services.sheet_validation import SheetValidationError, missing_required_fields, validate_sheet_data

SCHEMA = {
    "version": 1,
    "fields": {
        "character_name": {"type": "string", "label": "Nome", "required": True},
        "level": {"type": "integer", "label": "Nível", "min": 1, "max": 30},
        "notes": {"type": "text", "label": "Notas"},
    },
}

CANVAS = {
    "role_overrides": {
        "player": {"readonly_fields": ["level"]},
        "gm": {"readonly_fields": []},
    }
}


def test_validate_required_field():
    with pytest.raises(SheetValidationError):
        validate_sheet_data(SCHEMA, {})


def test_validate_integer_bounds():
    with pytest.raises(SheetValidationError):
        validate_sheet_data(SCHEMA, {"character_name": "X", "level": 99})


def test_missing_required_fields():
    missing = missing_required_fields(SCHEMA, {"level": 5})
    assert "Nome" in missing


def test_player_cannot_edit_level():
    perms = field_permissions(CANVAS, "player", SCHEMA["fields"])
    assert perms["character_name"] is True
    assert perms["level"] is False


def test_gm_can_edit_all():
    perms = field_permissions(CANVAS, "gm", SCHEMA["fields"])
    assert all(perms.values())


def test_readonly_fields_for_player():
    ro = readonly_fields_for_role(CANVAS, "player")
    assert "level" in ro
