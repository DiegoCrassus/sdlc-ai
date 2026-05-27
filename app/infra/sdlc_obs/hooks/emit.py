"""
Shared emitter — thin wrapper around Collector with state file for run_id continuity.

The state file (.sdlc_obs_state.json in the repo root) allows pre_task.py and
post_task.py to share the current run_id without passing it on the command line.
"""

import json
import os
from pathlib import Path

_STATE_FILE = Path(os.environ.get("SDLC_OBS_STATE",
                                  Path(__file__).parents[4] / ".sdlc_obs_state.json"))


def write_state(run_id: str, extra: dict | None = None) -> None:
    data = {"run_id": run_id, **(extra or {})}
    _STATE_FILE.write_text(json.dumps(data))


def read_state() -> dict:
    if not _STATE_FILE.exists():
        return {}
    try:
        return json.loads(_STATE_FILE.read_text())
    except Exception:
        return {}


def clear_state() -> None:
    if _STATE_FILE.exists():
        _STATE_FILE.unlink()
