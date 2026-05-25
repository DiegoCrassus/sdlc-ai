#!/usr/bin/env python3
"""Convert a markdown file to HTML for Plane wiki pages."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError as exc:
    raise SystemExit("markdown package required: pip install markdown") from exc


def md_to_html(source: str, *, repo_path: str | None = None) -> str:
    body = markdown.markdown(
        source,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    footer = ""
    if repo_path:
        footer = (
            f'<hr/><p><em>Fonte: <code>{html.escape(repo_path)}</code> '
            f"(sincronizado via .sdlc/scripts/plane-sync-wiki-doc.sh)</em></p>"
        )
    return f"{body}{footer}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown to HTML for Plane wiki")
    parser.add_argument("file", type=Path, help="Markdown file path")
    parser.add_argument("--repo-path", help="Relative repo path shown in footer")
    parser.add_argument("-o", "--output", type=Path, help="Write HTML to file instead of stdout")
    args = parser.parse_args()

    text = args.file.read_text(encoding="utf-8")
    repo_path = args.repo_path or str(args.file.as_posix()).replace("\\", "/")
    html_out = md_to_html(text, repo_path=repo_path)
    if args.output:
        args.output.write_text(html_out, encoding="utf-8")
    else:
        sys.stdout.buffer.write(html_out.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
