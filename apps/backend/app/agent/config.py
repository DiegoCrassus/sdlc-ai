"""Deep Agent configuration — LLM settings and runtime toggles.

The agent uses GPT-4o-mini by default and degrades gracefully when
OPENAI_API_KEY is absent: every call returns a stub response so the
rest of the backend never breaks because of a missing credential.
"""

from __future__ import annotations

import os

# Model used by all agents unless overridden per call.
AGENT_MODEL: str = os.getenv("DEEP_AGENT_MODEL", "gpt-4o-mini")

# Max tokens returned in a single agent response.
AGENT_MAX_TOKENS: int = int(os.getenv("DEEP_AGENT_MAX_TOKENS", "1024"))

# Temperature: 0 keeps outputs deterministic for SDLC tasks.
AGENT_TEMPERATURE: float = float(os.getenv("DEEP_AGENT_TEMPERATURE", "0.0"))

# Feature flag — True when the API key is present at import time.
AGENT_ENABLED: bool = bool(os.getenv("OPENAI_API_KEY", ""))
