#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

PYTHON="$(resolve_python)"
cd "$SDLC_REPO_ROOT/apps/backend"
exec "$PYTHON" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
