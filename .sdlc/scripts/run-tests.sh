#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

PYTHON="$(resolve_python)"
export PYTHONPATH="$SDLC_REPO_ROOT/apps/backend"
"$PYTHON" -m pytest "$SDLC_REPO_ROOT/tests" -q
