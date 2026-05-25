#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
PYTHON="$(resolve_python)"
exec "$PYTHON" "$SDLC_REPO_ROOT/apps/backend/scripts/smoke_test.py"
