#!/usr/bin/env bash
# Shared helpers for .sdlc/scripts/*.sh
set -euo pipefail

_sdlc_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SDLC_REPO_ROOT="$(cd "$_sdlc_script_dir/../.." && pwd)"

# shellcheck source=/dev/null
source "$SDLC_REPO_ROOT/.sdlc/scripts/_load-env.sh"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: $1 not found. $2" >&2
    exit 1
  fi
}

_sdlc_unix_shell() {
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) return 1 ;;
    *) return 0 ;;
  esac
}

resolve_python() {
  local backend_venv="$SDLC_REPO_ROOT/apps/backend/.venv"
  local unix_candidates=(
    "$backend_venv/bin/python"
  )
  local win_candidates=(
    "$backend_venv/Scripts/python.exe"
  )
  local candidates=()

  if _sdlc_unix_shell; then
    candidates=("${unix_candidates[@]}")
  else
    candidates=("${win_candidates[@]}" "${unix_candidates[@]}")
  fi

  local c
  for c in "${candidates[@]}"; do
    if [[ -x "$c" ]]; then
      echo "$c"
      return 0
    fi
  done

  if _sdlc_unix_shell; then
    for c in "${win_candidates[@]}"; do
      if [[ -f "$c" ]]; then
        echo "error: Windows venv detected under Unix shell. Run: make setup" >&2
        return 1
      fi
    done
  fi

  echo "error: backend venv not found. Run: make setup" >&2
  return 1
}
