#!/usr/bin/env python3
"""
pre_task hook — opens a new SDLC observability run.

Called at the start of every agent task. Records the run start time
and stores the run_id in .sdlc_obs_state.json for post_task.py to pick up.

Usage:
    python app/infra/sdlc_obs/hooks/pre_task.py \
        --task    "[AI][BACKEND] Add Plane endpoint" \
        --stage   implementation \
        --agent   implementer \
        --tags    "[AI]" "[BACKEND]"

Environment:
    SDLC_OBS_DB    path to SQLite file (default: app/infra/sdlc_obs/data/sdlc_obs.db)
    SDLC_OBS_STATE path to state JSON  (default: .sdlc_obs_state.json)
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[4]))  # repo root

from app.infra.sdlc_obs.collector import Collector  # type: ignore
from app.infra.sdlc_obs.hooks.emit import write_state  # type: ignore


def main():
    p = argparse.ArgumentParser(description="Start an SDLC observability run")
    p.add_argument("--task",  required=True, help='Task name e.g. "[AI][BACKEND] Add endpoint"')
    p.add_argument("--stage", required=True, help="SDLC stage id")
    p.add_argument("--agent", required=True, help="Agent id")
    p.add_argument("--tags",  nargs="*",     help="Task tags e.g. [AI] [BACKEND]")
    p.add_argument("--notes", default="",    help="Optional notes")
    p.add_argument("--db",    default=None,  help="Override DB path")
    args = p.parse_args()

    db_path = args.db or os.environ.get("SDLC_OBS_DB")
    col = Collector(db_path=db_path)

    run_id = col.start_run(
        task_name=args.task,
        stage=args.stage,
        agent=args.agent,
        task_tags=args.tags or [],
        notes=args.notes,
    )

    write_state(run_id, {"task": args.task, "stage": args.stage, "agent": args.agent})
    print(f"[obs] run started: {run_id}")
    print(f"[obs] task: {args.task} | stage: {args.stage} | agent: {args.agent}")


if __name__ == "__main__":
    main()
