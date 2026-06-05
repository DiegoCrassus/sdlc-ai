"""Portfolio shared contract schema validation (INVES-117)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

PORTFOLIO_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "portfolio.schema.json"
)

SAMPLE_SNAPSHOT = {
    "snapshot_date": "2026-06-05",
    "total_value": 12500.5,
    "created_at": "2026-06-05T12:00:00Z",
    "updated_at": "2026-06-05T18:30:00Z",
}

SAMPLE_HISTORY_POINT = {
    "snapshot_date": "2026-06-05",
    "total_value": 12500.5,
    "daily_change_pct": 1.25,
    "cumulative_return_pct": 0.0,
}


def _load_portfolio_schema() -> dict[str, Any]:
    return json.loads(PORTFOLIO_SCHEMA_PATH.read_text(encoding="utf-8"))


def _def_schema(name: str) -> dict[str, Any]:
    base = _load_portfolio_schema()
    return {
        "$schema": base["$schema"],
        "$ref": f"#/$defs/{name}",
        "$defs": base["$defs"],
    }


def test_portfolio_schema_is_valid_json_schema() -> None:
    schema = _load_portfolio_schema()
    jsonschema.Draft202012Validator.check_schema(schema)


def test_portfolio_snapshot_validates() -> None:
    jsonschema.validate(instance=SAMPLE_SNAPSHOT, schema=_def_schema("PortfolioSnapshot"))


def test_portfolio_history_point_validates() -> None:
    jsonschema.validate(
        instance=SAMPLE_HISTORY_POINT,
        schema=_def_schema("PortfolioHistoryPoint"),
    )


def test_portfolio_history_response_validates_without_summary() -> None:
    jsonschema.validate(
        instance={"days": 30, "points": [SAMPLE_HISTORY_POINT]},
        schema=_def_schema("PortfolioHistoryResponse"),
    )


def test_portfolio_history_response_validates_with_summary() -> None:
    jsonschema.validate(
        instance={
            "days": 90,
            "points": [SAMPLE_HISTORY_POINT],
            "summary": {
                "pnl_today": 150.25,
                "pnl_7d": 420.0,
                "pnl_30d": -80.5,
                "pnl_ytd": 1200.75,
            },
        },
        schema=_def_schema("PortfolioHistoryResponse"),
    )


def test_create_snapshot_response_validates() -> None:
    jsonschema.validate(
        instance={"snapshot": SAMPLE_SNAPSHOT, "created": True},
        schema=_def_schema("CreateSnapshotResponse"),
    )


def test_documented_endpoints_align_with_portfolio_api_paths() -> None:
    schema = _load_portfolio_schema()
    defs = schema["$defs"]
    assert "/api/v1/portfolio/history" in defs["PortfolioHistoryResponse"]["description"]
    assert "/api/v1/portfolio/snapshots" in defs["CreateSnapshotResponse"]["description"]
