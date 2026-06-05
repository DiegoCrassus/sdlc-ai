"""Auth shared contract schema validation (INVES-113)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

AUTH_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "auth.schema.json"
)

SAMPLE_USER = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
}


def _load_auth_schema() -> dict[str, Any]:
    return json.loads(AUTH_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_auth_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


def test_auth_schema_is_valid_json_schema() -> None:
    schema = _load_auth_schema()
    jsonschema.Draft202012Validator.check_schema(schema)


def test_identify_request_validates() -> None:
    jsonschema.validate(
        instance={"email": "user@example.com"},
        schema=_def_schema("IdentifyRequest"),
    )


def test_identify_response_validates() -> None:
    jsonschema.validate(
        instance={"user": SAMPLE_USER},
        schema=_def_schema("IdentifyResponse"),
    )


def test_auth_me_response_validates() -> None:
    jsonschema.validate(
        instance={"user": SAMPLE_USER},
        schema=_def_schema("AuthMeResponse"),
    )


def test_session_error_validates() -> None:
    jsonschema.validate(
        instance={"error": {"code": "UNAUTHORIZED", "message": "Missing session"}},
        schema=_def_schema("SessionError"),
    )


def test_logout_success_documents_204() -> None:
    schema = _load_auth_schema()
    logout = schema["$defs"]["LogoutSuccess"]
    assert "204" in logout["description"]
    assert "/api/v1/auth/logout" in logout["description"]
    jsonschema.validate(instance=None, schema=_def_schema("LogoutSuccess"))


def test_documented_endpoints_align_with_auth_api_paths() -> None:
    schema = _load_auth_schema()
    defs = schema["$defs"]
    for name, path in (
        ("IdentifyResponse", "/api/v1/auth/identify"),
        ("AuthMeResponse", "/api/v1/auth/me"),
        ("LogoutSuccess", "/api/v1/auth/logout"),
    ):
        assert path in defs[name]["description"]
