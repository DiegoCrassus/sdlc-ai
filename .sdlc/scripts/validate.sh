#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

cd "$SDLC_REPO_ROOT"
echo "== RPG-OP SDLC validate =="

PYTHON="$(resolve_python)"
export PYTHONPATH="$SDLC_REPO_ROOT/apps/backend"

"$PYTHON" -c "from app.main import app; print('backend import ok', app.title)"

if "$PYTHON" - <<'PY'
from urllib import request

try:
    request.urlopen("http://127.0.0.1:8000/health", timeout=1).read()
except Exception:
    raise SystemExit(1)
PY
then
  "$PYTHON" "$SDLC_REPO_ROOT/apps/backend/scripts/smoke_test.py"
else
  echo "skip: backend smoke (server is not running at 127.0.0.1:8000)"
fi

echo "== done =="
