#!/usr/bin/env python3
"""CLI for SDLC session gate — open, close, status, check."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".sdlc" / "dsl"))

import gate as _gate  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="SDLC session gate")
    sub = parser.add_subparsers(dest="command", required=True)

    o = sub.add_parser("open", help="Open gate for a card/stage")
    o.add_argument("--card", required=True)
    o.add_argument("--branch", default="")
    o.add_argument("--stage", required=True)
    o.add_argument("--intent", default="")

    sub.add_parser("close", help="Close gate")
    sub.add_parser("status", help="Print gate status")

    c = sub.add_parser("check", help="Check if path is writable")
    c.add_argument("--path", required=True)

    args = parser.parse_args()

    if args.command == "open":
        state = _gate.open_gate(
            card=args.card,
            branch=args.branch,
            stage=args.stage,
            intent=args.intent,
        )
        print(f"OK: gate open — {state.card} stage={state.stage}")
    elif args.command == "close":
        _gate.close_gate()
        print("OK: gate closed")
    elif args.command == "status":
        print(_gate.gate_status_text())
    elif args.command == "check":
        ok, msg = _gate.check_write(args.path)
        if ok:
            print(f"OK: {msg}")
        else:
            print(f"DENY: {msg}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
