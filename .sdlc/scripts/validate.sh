#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "== RPG-OP SDLC validate =="

if command -v rpg >/dev/null 2>&1; then
  rpg validate specs/
else
  echo "skip: rpg CLI not installed"
fi

if [[ -x backend/.venv/bin/python ]]; then
  backend/.venv/bin/python backend/scripts/smoke_test.py
else
  echo "skip: backend venv not found"
fi

echo "== done =="
