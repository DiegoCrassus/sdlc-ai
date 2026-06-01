#!/usr/bin/env python3
"""Autonomous squash-merge of a PR into develop when CI is green.

No human approval required when all gates pass (see auto-merge-policy.md).

Usage:
  python3 .sdlc/scripts/auto_merge_pr.py --pr 32
  python3 .sdlc/scripts/auto_merge_pr.py --branch feature/INVES-20-market-data
  python3 .sdlc/scripts/auto_merge_pr.py --pr 32 --card INVES-20 --plane-comment --evidence-file .sdlc/templates/plane/evidence-template.json
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
GITHUB_API = "https://api.github.com"
CARD_RE = re.compile(r"^INVES-\d+$", re.IGNORECASE)


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _github_token() -> tuple[str, str]:
    _load_dotenv()
    token = (
        os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC")
        or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
        or os.environ.get("GH_TOKEN")
    )
    repo = os.environ.get("GITHUB_REPOSITORY", "DiegoCrassus/sdlc-ai")
    if not token:
        print("ERROR: GitHub token not set (GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC)", file=sys.stderr)
        sys.exit(1)
    return token, repo


def _gh_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def find_pr_by_branch(token: str, repo: str, branch: str) -> int:
    owner, name = repo.split("/", 1)
    url = f"{GITHUB_API}/repos/{repo}/pulls"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            url,
            headers=_gh_headers(token),
            params={"head": f"{owner}:{branch}", "state": "open", "base": "develop"},
        )
        resp.raise_for_status()
        pulls = resp.json()
        if not pulls:
            print(f"ERROR: no open PR for branch {branch}", file=sys.stderr)
            sys.exit(1)
        return pulls[0]["number"]


def get_pr(token: str, repo: str, pr_number: int) -> dict:
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_gh_headers(token))
        resp.raise_for_status()
        return resp.json()


def wait_for_ci(token: str, repo: str, branch: str, timeout_sec: int, poll_sec: int) -> bool:
    deadline = time.time() + timeout_sec
    url = f"{GITHUB_API}/repos/{repo}/actions/runs"
    with httpx.Client(timeout=30.0) as client:
        while time.time() < deadline:
            resp = client.get(
                url,
                headers=_gh_headers(token),
                params={"branch": branch, "per_page": 5},
            )
            resp.raise_for_status()
            runs = resp.json().get("workflow_runs", [])
            if not runs:
                time.sleep(poll_sec)
                continue
            latest = runs[0]
            status = latest.get("status")
            conclusion = latest.get("conclusion")
            print(f"CI: {latest.get('name')} status={status} conclusion={conclusion}")
            if status == "completed":
                return conclusion == "success"
            time.sleep(poll_sec)
    print("ERROR: CI wait timeout", file=sys.stderr)
    return False


def merge_pr(token: str, repo: str, pr_number: int, title: str | None) -> dict:
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/merge"
    body: dict = {"merge_method": "squash"}
    if title:
        body["commit_title"] = title
    with httpx.Client(timeout=60.0) as client:
        resp = client.put(url, headers=_gh_headers(token), json=body)
        if resp.status_code == 405:
            print(f"ERROR: merge not allowed — {resp.json().get('message')}", file=sys.stderr)
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()


def delete_branch(token: str, repo: str, branch: str) -> None:
    if branch in ("develop", "main"):
        return
    url = f"{GITHUB_API}/repos/{repo}/git/refs/heads/{branch}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.delete(url, headers=_gh_headers(token))
        if resp.status_code in (204, 404):
            print(f"OK: branch {branch} deleted (or already gone)")
        else:
            print(f"WARN: could not delete branch {branch}: {resp.status_code}", file=sys.stderr)


def plane_done(card: str, pr_url: str, pr_number: int, evidence_file: str | None = None) -> None:
    import json
    import subprocess

    script = ROOT / ".sdlc/scripts/plane_state.py"
    ev_path = evidence_file
    if not ev_path:
        default = ROOT / ".sdlc/templates/plane" / f"evidence-{card.upper()}.json"
        if default.is_file():
            ev_path = str(default)

    if ev_path and Path(ev_path).is_file():
        data = json.loads(Path(ev_path).read_text(encoding="utf-8"))
        art = data.setdefault("artifacts", {})
        art.setdefault("pr", str(pr_number))
        art.setdefault("pr_url", pr_url)
        tmp = ROOT / ".sdlc/memory/.plane-evidence-tmp.json"
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        subprocess.run(
            [
                sys.executable,
                str(script),
                "done",
                "--card",
                card,
                "--evidence-file",
                str(tmp),
            ],
            check=True,
            cwd=ROOT,
        )
        tmp.unlink(missing_ok=True)
        return

    subprocess.run(
        [
            sys.executable,
            str(script),
            "done",
            "--card",
            card,
            "--comment",
            f"Autonomous merge — PR #{pr_number}: {pr_url}",
        ],
        check=True,
        cwd=ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous PR squash merge")
    parser.add_argument("--pr", type=int, help="Pull request number")
    parser.add_argument("--branch", help="Head branch name")
    parser.add_argument("--card", help="Plane card INVES-N for Done transition")
    parser.add_argument("--plane-comment", action="store_true", help="Move Plane card to Done")
    parser.add_argument(
        "--evidence-file",
        default="",
        help="Structured JSON evidence for Plane Done comment",
    )
    parser.add_argument("--timeout", type=int, default=600, help="CI wait seconds")
    parser.add_argument("--poll", type=int, default=15, help="CI poll interval")
    parser.add_argument("--skip-ci-wait", action="store_true", help="Merge immediately (dangerous)")
    args = parser.parse_args()

    token, repo = _github_token()
    if not args.pr and not args.branch:
        print("ERROR: provide --pr or --branch", file=sys.stderr)
        sys.exit(1)

    pr_number = args.pr or find_pr_by_branch(token, repo, args.branch)
    pr = get_pr(token, repo, pr_number)
    branch = pr["head"]["ref"]
    pr_url = pr["html_url"]

    if pr.get("merged"):
        print(f"Already merged: {pr_url}")
        if args.plane_comment and args.card:
            plane_done(
                args.card,
                pr_url,
                pr_number,
                args.evidence_file or None,
            )
        sys.exit(0)

    if pr.get("mergeable") is False and pr.get("mergeable_state") == "dirty":
        print("ERROR: PR has merge conflicts", file=sys.stderr)
        sys.exit(1)

    if not args.skip_ci_wait:
        if not wait_for_ci(token, repo, branch, args.timeout, args.poll):
            print("ERROR: CI not green — merge blocked", file=sys.stderr)
            sys.exit(1)

    title = pr.get("title")
    result = merge_pr(token, repo, pr_number, title)
    if not result.get("merged"):
        print(f"ERROR: merge failed — {result}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: merged PR #{pr_number} -> develop")
    delete_branch(token, repo, branch)

    if args.card and CARD_RE.match(args.card):
        if args.plane_comment:
            plane_done(
                args.card,
                pr_url,
                pr_number,
                args.evidence_file or None,
            )
        else:
            print(f"Hint: run plane_state.py done --card {args.card}")


if __name__ == "__main__":
    main()
