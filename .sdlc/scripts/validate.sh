#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

cd "$SDLC_REPO_ROOT"
echo "== RPG-OP SDLC validate =="

if command -v rpg >/dev/null 2>&1; then
  rpg validate specs/
elif PYTHON="$(resolve_python)" && "$PYTHON" -c "import rpg_dsl" 2>/dev/null; then
  "$PYTHON" -m rpg_dsl._cli validate specs/
else
  echo "skip: rpg_dsl not installed — run: pip install -e packages/rpg_dsl"
fi

PYTHON="$(resolve_python)"
SMOKE_PY="$SDLC_REPO_ROOT/apps/backend/scripts/smoke_test.py"
if [[ -x "$PYTHON" || -f "$PYTHON" ]]; then
  "$PYTHON" "$SMOKE_PY" || true
else
  echo "skip: backend venv not found (run: make setup)"
fi

echo "== done =="
