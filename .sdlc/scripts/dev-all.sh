#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

BACKEND_DIR="$SDLC_REPO_ROOT/apps/backend"
FRONTEND_DIR="$SDLC_REPO_ROOT/apps/frontend"
PYTHON="$(resolve_python)"

require_cmd npm "Install Node.js 20+"

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "Installing frontend dependencies..."
  (cd "$FRONTEND_DIR" && npm install)
fi

echo ""
echo "== RPG-OP dev =="
echo "Backend : http://127.0.0.1:8000  (API /v1/workspaces)"
echo "Frontend: http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both."
echo ""

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

(cd "$BACKEND_DIR" && "$PYTHON" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
BACKEND_PID=$!

cd "$FRONTEND_DIR"
npm run dev
