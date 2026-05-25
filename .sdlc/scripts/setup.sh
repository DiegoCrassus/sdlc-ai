#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

require_cmd uv "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
require_cmd npm "Install Node.js 20+"

BACKEND="$SDLC_REPO_ROOT/apps/backend"
FRONTEND="$SDLC_REPO_ROOT/apps/frontend"

if _sdlc_unix_shell && [[ -f "$BACKEND/.venv/Scripts/python.exe" && ! -x "$BACKEND/.venv/bin/python" ]]; then
  echo "== Recreating Linux venv (Windows venv is not usable from bash/WSL) =="
  rm -rf "$BACKEND/.venv"
fi

if ! PYTHON="$(resolve_python)"; then
  echo "== Backend venv =="
  uv venv "$BACKEND/.venv" --python 3.12
  PYTHON="$(resolve_python)"
fi

echo "== Backend deps =="
uv pip install --python "$PYTHON" -r "$BACKEND/requirements.txt" pytest

echo "== Frontend deps =="
(cd "$FRONTEND" && npm install)

echo "Setup complete."
