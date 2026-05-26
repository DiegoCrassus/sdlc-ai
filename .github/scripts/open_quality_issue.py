"""Create or update a GitHub issue for CI quality failures."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TOKEN = os.environ["SDLC_PAT_CLASSIC"]
REPO = os.environ["REPO"]
CHECK_KIND = os.environ.get("CHECK_KIND", "quality")
COMMIT_SHA = os.environ.get("COMMIT_SHA", "")[:7]
COMMIT_MSG = os.environ.get("COMMIT_MSG", "").split("\n")[0][:80]
BRANCH = os.environ.get("BRANCH", "unknown")
RUN_URL = os.environ.get("RUN_URL", "")

PY_ERRORS = os.environ.get("PYTHON_ERRORS", "").replace("%0A", "\n")
TS_ERRORS = os.environ.get("TS_ERRORS", "").replace("%0A", "\n")
TEST_ERRORS = os.environ.get("TEST_ERRORS", "").replace("%0A", "\n")

PY_FAILED = os.environ.get("PYTHON_FAILED", "false") == "true"
TS_FAILED = os.environ.get("TS_FAILED", "false") == "true"
TEST_FAILED = os.environ.get("TEST_FAILED", "false") == "true"

BASE = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def api(method: str, path: str, body: dict | None = None) -> tuple[int, dict | list]:
    data = json.dumps(body).encode() if body else None
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        try:
            payload: dict | list = json.loads(exc.read())
        except Exception:
            payload = {}
        return exc.code, payload


def ensure_label(name: str, color: str, description: str) -> None:
    status, _ = api("GET", f"/labels/{name}")
    if status == 404:
        api("POST", "/labels", {"name": name, "color": color, "description": description})


def find_open_issue(title_prefix: str, label: str) -> int | None:
    status, data = api("GET", f"/issues?state=open&labels={label}&per_page=30")
    if status != 200 or not isinstance(data, list):
        return None
    for issue in data:
        if issue.get("title", "").startswith(title_prefix):
            return issue["number"]
    return None


def section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return f"## {title}\n\n```\n{body.strip()}\n```"


labels = {
    "lint": ("sdlc:lint-fail", "E4E669", "Lint failed and needs correction"),
    "test": ("sdlc:test-fail", "D93F0B", "Unit tests failed and need correction"),
}
primary_label, color, description = labels.get(
    CHECK_KIND, ("sdlc:ci-fail", "B60205", "GitHub Actions failed and need correction")
)

ensure_label("sdlc:ci-fail", "B60205", "GitHub Actions failed and need correction")
ensure_label(primary_label, color, description)
ensure_label("sdlc:blocked", "B60205", "Blocked and needs human or agent intervention")

sections = [
    section("Python — ruff", PY_ERRORS) if PY_FAILED else "",
    section("TypeScript — build/typecheck", TS_ERRORS) if TS_FAILED else "",
    section("Unit tests — pytest", TEST_ERRORS) if TEST_FAILED else "",
]
details = "\n\n".join(item for item in sections if item)

body = f"""\
## CI quality failure on `{COMMIT_SHA}`

**Kind:** `{CHECK_KIND}`
**Branch:** `{BRANCH}`
**Commit:** {COMMIT_MSG}
**Run:** {RUN_URL}

{details}

## Required flow

1. `issue-resolver` investigates the root cause.
2. The smallest safe fix is pushed to the same PR branch.
3. GitHub Actions re-run lint and unit tests.
4. This issue is closed only after checks are green on the latest head SHA.

---
Created automatically by GitHub Actions.
"""

title = f"[{CHECK_KIND}-fail] {BRANCH} - {COMMIT_SHA}: {COMMIT_MSG}"[:120]
existing = find_open_issue(f"[{CHECK_KIND}-fail] {BRANCH}", primary_label)

if existing:
    api(
        "POST",
        f"/issues/{existing}/comments",
        {"body": f"### New failure on `{COMMIT_SHA}`\n\n{details}\n\n[Run]({RUN_URL})"},
    )
    issue_number = existing
    print(f"Updated existing issue #{existing}")
else:
    status, issue = api(
        "POST",
        "/issues",
        {"title": title, "body": body, "labels": ["sdlc:ci-fail", primary_label, "type:bug"]},
    )
    if status not in (200, 201) or not isinstance(issue, dict):
        print(f"Failed to create issue: {status} {issue}", file=sys.stderr)
        sys.exit(1)
    issue_number = issue["number"]
    print(f"Created issue #{issue_number}: {title}")

output_file = os.environ.get("GITHUB_OUTPUT", "")
if output_file:
    with open(output_file, "a", encoding="utf-8") as file:
        file.write(f"issue_number={issue_number}\n")
