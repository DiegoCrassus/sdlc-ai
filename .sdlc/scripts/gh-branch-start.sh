#!/usr/bin/env bash
# Create and switch to an SDLC branch from a Plane task identifier.
# Usage: gh-branch-start.sh <feature|bugfix> <RPG-123>
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

require_cmd git "Install git: https://git-scm.com/"

KIND="${1:?Usage: gh-branch-start.sh <feature|bugfix> <RPG-123>}"
TASK_ID="${2:?Usage: gh-branch-start.sh <feature|bugfix> <RPG-123>}"
BASE="develop"

if [[ $# -gt 2 ]]; then
  echo "error: base branch is fixed to 'develop'; do not pass a custom base" >&2
  exit 1
fi

case "$KIND" in
  feature|bugfix) ;;
  *)
    echo "error: kind must be 'feature' or 'bugfix', got '$KIND'" >&2
    exit 1
    ;;
esac

if [[ ! "$TASK_ID" =~ ^[A-Za-z]+-[0-9]+$ ]]; then
  echo "error: task id must match Plane identifier (e.g. RPG-123), got '$TASK_ID'" >&2
  exit 1
fi

if [[ "${PLANE_REQUIRED:-1}" == "1" ]]; then
  if [[ -z "${PLANE_API_KEY:-}" || -z "${PLANE_WORKSPACE_SLUG:-}" ]]; then
    echo "error: Plane task verification requires PLANE_API_KEY and PLANE_WORKSPACE_SLUG" >&2
    echo "hint: create/retrieve the Plane task first, then run ./launch.sh or source .env" >&2
    exit 1
  fi
fi

BRANCH="${KIND}/${TASK_ID}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: not a git repository" >&2
  exit 1
fi

if git status --porcelain | grep -q .; then
  echo "error: working tree has uncommitted changes; finish or stash them before starting a GitHub workflow" >&2
  exit 1
fi

CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT" == "$BRANCH" ]]; then
  echo "Already on branch $BRANCH"
  exit 0
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git switch "$BRANCH"
  echo "Switched to existing branch $BRANCH"
  exit 0
fi

if git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  git fetch origin "$BASE" --quiet 2>/dev/null || true
fi

if git show-ref --verify --quiet "refs/heads/$BASE"; then
  git switch "$BASE"
  git pull --ff-only origin "$BASE" 2>/dev/null || true
elif git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  git switch -c "$BASE" "origin/$BASE"
else
  echo "error: base branch '$BASE' not found locally or on origin" >&2
  exit 1
fi

git switch -c "$BRANCH"
echo "Created and switched to $BRANCH (from $BASE)"
