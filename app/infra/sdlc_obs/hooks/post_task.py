#!/usr/bin/env python3
"""
post_task hook — closes an SDLC observability run with outcome metrics.

Called at the end of every agent task. Reads run_id from .sdlc_obs_state.json
(written by pre_task.py) and records the final metrics.

Usage:
    python app/infra/sdlc_obs/hooks/post_task.py \
        --status      completed \
        --tokens-in   1200 \
        --tokens-out  800 \
        --cost        0.0048 \
        --tools-total 5 \
        --tools-ok    5 \
        --tests-pass  12 \
        --tests-fail  0 \
        --doctor      0

Flags:
    --hallucination    set hallucination_flag = 1
    --regression       set regression_flag = 1

Environment:
    SDLC_OBS_DB    path to SQLite file
    SDLC_OBS_STATE path to state JSON
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[4]))  # repo root

from app.infra.sdlc_obs.collector import Collector  # type: ignore
from app.infra.sdlc_obs.hooks.emit import clear_state, read_state  # type: ignore


def main():
    p = argparse.ArgumentParser(description="End an SDLC observability run")
    p.add_argument("--status",       default="completed",
                   choices=["completed","failed","escalated","abandoned","unknown"])
    p.add_argument("--tokens-in",    type=int,   default=0)
    p.add_argument("--tokens-out",   type=int,   default=0)
    p.add_argument("--cost",         type=float, default=0.0,   help="USD")
    p.add_argument("--tools-total",  type=int,   default=0)
    p.add_argument("--tools-ok",     type=int,   default=0)
    p.add_argument("--tools-fail",   type=int,   default=0)
    p.add_argument("--doctor",       type=int,   default=None,  help="Doctor exit code (0|1)")
    p.add_argument("--tests-pass",   type=int,   default=0)
    p.add_argument("--tests-fail",   type=int,   default=0)
    p.add_argument("--hallucination",action="store_true")
    p.add_argument("--regression",   action="store_true")
    p.add_argument("--notes",        default="")
    p.add_argument("--run-id",       default=None, help="Override run_id (skip state file)")
    p.add_argument("--db",           default=None)
    args = p.parse_args()

    state = read_state()
    run_id = args.run_id or state.get("run_id")
    if not run_id:
        print("[obs] ERROR: no run_id found. Run pre_task.py first or pass --run-id", file=sys.stderr)
        sys.exit(1)

    db_path = args.db or os.environ.get("SDLC_OBS_DB")
    col = Collector(db_path=db_path)

    col.end_run(
        run_id=run_id,
        completion_status=args.status,
        tokens_input=args.tokens_in,
        tokens_output=args.tokens_out,
        cost_usd=args.cost,
        tool_calls_total=args.tools_total,
        tool_calls_success=args.tools_ok,
        tool_calls_failed=args.tools_fail,
        doctor_exit_code=args.doctor,
        tests_passed=args.tests_pass,
        tests_failed=args.tests_fail,
        hallucination_flag=args.hallucination,
        regression_flag=args.regression,
        notes=args.notes,
    )

    clear_state()
    print(f"[obs] run closed: {run_id} → {args.status}")
    print(f"[obs] cost: ${args.cost:.4f} | tokens: {args.tokens_in}+{args.tokens_out}"
          f" | tools: {args.tools_ok}/{args.tools_total} | doctor: {args.doctor}")


if __name__ == "__main__":
    main()
