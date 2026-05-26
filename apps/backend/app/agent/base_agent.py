"""DeepAgent — base LangChain agent for SDLC-AI-Native tasks.

Architecture
------------
- Uses LangChain LCEL (LangChain Expression Language) to compose
  prompt → LLM → output parser into a single invocable chain.
- When OPENAI_API_KEY is missing the constructor sets ``_enabled=False``
  and ``invoke()`` returns a deterministic stub without raising.
- Subclasses override ``system_prompt`` to specialise the agent role.

Usage
-----
    from app.agent import DeepAgent

    agent = DeepAgent()
    result = agent.invoke("Analise este template de ficha D&D.")
    print(result["output"])          # str
    print(result["model"])           # "gpt-4o-mini" | "stub"
    print(result["enabled"])         # True | False
"""

from __future__ import annotations

from typing import Any

from .config import AGENT_ENABLED, AGENT_MAX_TOKENS, AGENT_MODEL, AGENT_TEMPERATURE

_STUB_OUTPUT = (
    "[DeepAgent desabilitado] Configure OPENAI_API_KEY para ativar o agente LLM."
)


class DeepAgent:
    """Base agent — wraps a LangChain LCEL chain with graceful degradation."""

    system_prompt: str = (
        "Você é um agente especialista em SDLC AI-Native. "
        "Responda de forma concisa, em português, com foco em engenharia de software."
    )

    def __init__(self) -> None:
        self._enabled = AGENT_ENABLED
        self._chain: Any = None

        if self._enabled:
            self._chain = self._build_chain()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def invoke(self, user_message: str) -> dict[str, Any]:
        """Run the agent and return a structured result dict.

        Parameters
        ----------
        user_message:
            Plain-text instruction or question from the caller.

        Returns
        -------
        dict with keys:
            ``output`` (str), ``model`` (str), ``enabled`` (bool)
        """
        if not self._enabled or self._chain is None:
            return {"output": _STUB_OUTPUT, "model": "stub", "enabled": False}

        raw = self._chain.invoke({"input": user_message})
        return {
            "output": raw.content if hasattr(raw, "content") else str(raw),
            "model": AGENT_MODEL,
            "enabled": True,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_chain(self) -> Any:
        """Construct the LCEL chain (prompt | llm).

        Import is deferred so the module loads without error even when
        langchain-openai is not installed — the feature flag guards entry.
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=AGENT_MODEL,
                temperature=AGENT_TEMPERATURE,
                max_tokens=AGENT_MAX_TOKENS,
            )
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    ("human", "{input}"),
                ]
            )
            return prompt | llm
        except Exception:
            self._enabled = False
            return None
