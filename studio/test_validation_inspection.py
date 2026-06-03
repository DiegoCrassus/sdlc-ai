from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from studio import (
    ValidationInspectionInputError,
    ValidationRunResult,
    build_canvas_view_model,
    build_validation_inspection_from_sources,
    build_validation_inspection_model,
    compile_studio_sources,
    render_validation_inspection_text,
    validate_compiler_result,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_BODY_KEYS = {"body", "content", "prompt", "ci_log", "evidence", "coordinates", "props", "runtime_state"}
FORBIDDEN_OUTPUT_PATHS = ("studio/generated", "studio/examples", "specs")


def test_validation_inspection_is_deterministic_and_schema_shaped() -> None:
    before_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
    first = build_validation_inspection_from_sources(REPO_ROOT).to_dict()

    assert first == build_validation_inspection_from_sources(REPO_ROOT).to_dict()
    assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == before_exists
    assert set(first) == {"inspection", "summary", "groups", "records"}
    assert first["inspection"]["id"] == "inspection.sdlc_studio.validation"
    assert first["inspection"]["authority"] == "derived_non_authoritative"
    assert first["inspection"]["canvas_ref"] == "canvas.sdlc_studio.derived_graph"
    assert first["inspection"]["filters"] == {"status": None, "check_type": None, "target_type": None}
    assert first["summary"]["total_records"] == 6
    assert first["summary"]["visible_records"] == 6
    assert first["summary"]["by_status"] == {"pass": 6, "warn": 0, "fail": 0, "not_run": 0}
    assert [record["id"] for record in first["records"]] == sorted(record["id"] for record in first["records"])
    assert [group["id"] for group in first["groups"]] == sorted(group["id"] for group in first["groups"])
    _assert_forbidden_body_keys_absent(first)


def test_validation_inspection_preserves_record_refs_and_messages() -> None:
    payload = build_validation_inspection_from_sources(REPO_ROOT).to_dict()

    for record in payload["records"]:
        assert record["id"].startswith("inspection.record.")
        assert record["validation_ref"].startswith("validation.")
        assert record["status"] in {"pass", "warn", "fail", "not_run"}
        assert record["check_type"]
        assert set(record["target"]) == {"ref_type", "ref"}
        assert record["messages"]
        assert record["source_refs"]
        assert isinstance(record["related_display_refs"], list)
        assert 0 < len(record["summary"]) <= 180


def test_filters_and_grouping_are_reflected_in_metadata() -> None:
    model = build_validation_inspection_from_sources(
        REPO_ROOT,
        status="pass",
        check_type="policy",
        target_type="path",
        group_by="check_type",
    ).to_dict()

    assert model["inspection"]["filters"] == {"status": "pass", "check_type": "policy", "target_type": "path"}
    assert model["inspection"]["group_by"] == "check_type"
    assert model["summary"]["total_records"] == 6
    assert model["summary"]["visible_records"] == 2
    assert model["summary"]["by_check_type"] == {"policy": 2}
    assert [group["key"] for group in model["groups"]] == ["policy"]
    assert all(record["status"] == "pass" and record["check_type"] == "policy" for record in model["records"])
    assert all(record["target"]["ref_type"] == "path" for record in model["records"])


def test_grouping_by_target_type_includes_stable_record_ids() -> None:
    model = build_validation_inspection_from_sources(REPO_ROOT, group_by="target_type").to_dict()

    assert [group["key"] for group in model["groups"]] == ["graph", "path", "workflow"]
    for group in model["groups"]:
        assert group["group_by"] == "target_type"
        assert group["record_ids"] == sorted(group["record_ids"])
        assert group["count"] == len(group["record_ids"])


def test_text_rendering_declares_derived_non_authoritative_scope() -> None:
    text = render_validation_inspection_text(build_validation_inspection_from_sources(REPO_ROOT, status="pass"))

    assert "Studio validation inspection: derived, non-authoritative output" in text
    assert "authority: derived_non_authoritative" in text
    assert "filters: status=pass" in text
    assert "transient stdout/in-memory" in text


def test_visible_failures_are_counted_after_filters() -> None:
    compiled = compile_studio_sources(REPO_ROOT)
    base_validation = validate_compiler_result(compiled, REPO_ROOT)
    failed = _validation_record("validation.path.fail", "path", "studio/validation_inspection.py", "fail")
    validation = ValidationRunResult(
        results=(*base_validation.results, failed),
        summary={"pass": 6, "warn": 0, "fail": 1, "not_run": 0},
        report=base_validation.report,
    )
    canvas = build_canvas_view_model(compiled, validation)

    fail_model = build_validation_inspection_model(compiled, validation, canvas, status="fail").to_dict()
    pass_model = build_validation_inspection_model(compiled, validation, canvas, status="pass").to_dict()

    assert fail_model["summary"]["by_status"]["fail"] == 1
    assert [record["validation_ref"] for record in fail_model["records"]] == ["validation.path.fail"]
    assert pass_model["summary"]["by_status"]["fail"] == 0


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"status": "bad"}, "invalid status: bad"),
        ({"check_type": "bad"}, "invalid check_type: bad"),
        ({"target_type": "bad"}, "invalid target_type: bad"),
        ({"group_by": "bad"}, "invalid group_by: bad"),
    ],
)
def test_invalid_filters_and_grouping_raise_concise_errors(kwargs: dict[str, str], message: str) -> None:
    with pytest.raises(ValidationInspectionInputError, match=message):
        build_validation_inspection_from_sources(REPO_ROOT, **kwargs)


def _validation_record(record_id: str, target_type: str, target_ref: str, status: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "target_ref": {"ref_type": target_type, "ref": target_ref},
        "check_type": "custom",
        "status": status,
        "messages": [{"level": "error" if status == "fail" else "info", "text": f"{status} inspection record."}],
        "source_refs": [{"ref_type": "path", "ref": "studio/validation-result-ir-contract.md"}],
    }


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        assert not (set(value) & FORBIDDEN_BODY_KEYS)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)
