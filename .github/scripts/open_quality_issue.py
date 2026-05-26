"""Create or update a GitHub issue for CI quality failures (lint or tests).

Environment variables
---------------------
SDLC_PAT_CLASSIC  GitHub PAT with issues:write scope
REPO              owner/repo  (e.g. DiegoCrassus/sdlc-ai)
COMMIT_SHA        Full SHA of the failing commit
COMMIT_MSG        First line of the commit message
BRANCH            Branch that triggered the workflow
CHECK_KIND        "lint" | "test"
ERRORS            Combined error output from the failing check
RUN_URL           URL of the failing Actions run

Output (GITHUB_OUTPUT)
----------------------
issue_number      Number of the created/updated issue
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TOKEN      = os.environ["SDLC_PAT_CLASSIC"]
REPO       = os.environ["REPO"]
SHA        = os.environ.get("COMMIT_SHA", "")[:7]
MSG        = os.environ.get("COMMIT_MSG", "").split("\n")[0][:80]
BRANCH     = os.environ.get("BRANCH", "unknown")
KIND       = os.environ.get("CHECK_KIND", "lint")   # "lint" | "test"
ERRORS     = os.environ.get("ERRORS", "").replace("%0A", "\n")
RUN_URL    = os.environ.get("RUN_URL", "")

BASE    = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept":        "application/vnd.github+json",
    "Content-Type":  "application/json",
    "X-GitHub-Api-Version": "2022-11-28",
}

LABEL_MAP = {
    "lint": ("sdlc:lint-fail", "E4E669", "Lint failure — awaiting auto-fix"),
    "test": ("sdlc:test-fail", "D93F0B", "Test failure — awaiting auto-fix"),
}


def api(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(f"{BASE}{path}", data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}


def ensure_label(name: str, color: str, description: str) -> None:
    status, _ = api("GET", f"/labels/{name}")
    if status == 404:
        api("POST", "/labels", {"name": name, "color": color, "description": description})


def find_open_issue(title_prefix: str, label: str) -> int | None:
    status, data = api("GET", f"/issues?state=open&labels={label}&per_page=20")
    if status != 200:
        return None
    for issue in data:
        if issue.get("title", "").startswith(title_prefix):
            return issue["number"]
    return None


label_name, label_color, label_desc = LABEL_MAP.get(KIND, LABEL_MAP["lint"])
tag = "lint-fail" if KIND == "lint" else "test-fail"

error_block = f"```\n{ERRORS.strip()}\n```" if ERRORS.strip() else "_No details captured._"

body = f"""\
## `{KIND}` failed on commit `{SHA}`

**Branch:** `{BRANCH}`
**Commit:** {MSG}
**Run:** {RUN_URL}

{error_block}

---
> Auto-created by `{KIND}.yml`.  The Quality Fix Agent will attempt an automated correction.
> If the fix cannot be applied automatically, this issue will receive `sdlc:blocked`.
"""

title = f"[{tag}] {BRANCH} — {SHA}: {MSG}"[:120]

ensure_label(label_name, label_color, label_desc)

existing = find_open_issue(f"[{tag}] {BRANCH}", label_name)
if existing:
    api("POST", f"/issues/{existing}/comments", {
        "body": f"### New failure — `{SHA}`\n\n{error_block}\n\n[Run]({RUN_URL})"
    })
    issue_number = existing
    print(f"Updated existing issue #{existing}")
else:
    status, issue = api("POST", "/issues", {
        "title":  title,
        "body":   body,
        "labels": [label_name, "type:bug"],
    })
    if status not in (200, 201):
        print(f"Failed to create issue: {status}", file=sys.stderr)
        sys.exit(1)
    issue_number = issue["number"]
    print(f"Created issue #{issue_number}: {title}")

output_file = os.environ.get("GITHUB_OUTPUT", "")
if output_file:
    with open(output_file, "a") as f:
        f.write(f"issue_number={issue_number}\n")
