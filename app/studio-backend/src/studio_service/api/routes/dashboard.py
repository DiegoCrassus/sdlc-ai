from __future__ import annotations

from fastapi import APIRouter

from studio_service.deps import EngineSvc, RepoRoot
from studio_service.services.session_reader import read_handoff, read_session_gate

router = APIRouter(prefix="/dashboard", tags=["s1-dashboard"])


@router.get("/summary")
def dashboard_summary(repo_root: RepoRoot, engine: EngineSvc) -> dict:
    readiness = engine.readiness(repo_root)
    gate_doc = read_session_gate(repo_root)
    handoff_doc = read_handoff(repo_root)
    canvas_counts = _canvas_counts(engine, repo_root)
    summary = readiness.get("summary", {})
    readiness_meta = readiness.get("readiness", {})
    gate = gate_doc.get("gate") or {}
    routing = handoff_doc.get("sections", {}).get("Routing", {})
    return {
        "authority": readiness_meta.get("authority"),
        "readiness": {
            "overall_status": readiness_meta.get("overall_status"),
            "mvp_ready": summary.get("mvp_ready"),
            "pass": summary.get("pass"),
            "warn": summary.get("warn"),
            "fail": summary.get("fail"),
        },
        "session": {
            "gate_open": gate.get("gate_status") == "open",
            "card": gate.get("card"),
            "branch": gate.get("branch"),
            "stage": gate.get("stage"),
            "next_agent": routing.get("Next agent"),
            "stage_complete": routing.get("Stage complete"),
        },
        "canvas": canvas_counts,
        "handoff_present": handoff_doc.get("present", False),
    }


def _canvas_counts(engine, repo_root) -> dict:
    from studio_service.api.errors import StudioApiError

    try:
        canvas = engine.canvas(repo_root)
    except StudioApiError:
        return {"nodes": 0, "edges": 0, "available": False}
    return {
        "available": True,
        "nodes": len(canvas.get("nodes", [])),
        "edges": len(canvas.get("edges", [])),
        "validation_statuses": (canvas.get("legend") or {}).get("validation_statuses", {}),
    }
