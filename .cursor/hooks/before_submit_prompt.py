"""Pre-hook: beforeSubmitPrompt — audit prompt, block obvious secrets."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib.langsmith_emit import SECRET_PATTERNS, emit_pre, read_stdin, respond, sanitize


def main() -> None:
    data = read_stdin()
    prompt = str(data.get("prompt") or data.get("text") or "")
    emit_pre("beforeSubmitPrompt", {"prompt_preview": sanitize(prompt, 300)})

    for pattern in SECRET_PATTERNS:
        if pattern.search(prompt):
            respond(
                {
                    "continue": False,
                    "user_message": "O prompt parece conter um token/secret. Remova antes de enviar.",
                }
            )

    respond({"continue": True})


if __name__ == "__main__":
    main()
