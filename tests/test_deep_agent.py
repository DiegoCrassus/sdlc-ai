"""Unit tests for the Deep Agent base module (RPG-81).

All tests run without an OPENAI_API_KEY — the agent must degrade
gracefully and return a stub response rather than raising.
"""

from __future__ import annotations

import importlib
import os
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reload_agent_module():
    """Reload agent modules so config picks up monkeypatched env vars."""
    import app.agent.base_agent as ba_mod
    import app.agent.config as cfg_mod

    importlib.reload(cfg_mod)
    importlib.reload(ba_mod)
    import app.agent as pkg

    importlib.reload(pkg)
    return pkg


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------


class TestAgentConfig:
    def test_defaults(self):
        from app.agent.config import (
            AGENT_MAX_TOKENS,
            AGENT_MODEL,
            AGENT_TEMPERATURE,
        )

        assert AGENT_MODEL == "gpt-4o-mini"
        assert AGENT_MAX_TOKENS == 1024
        assert AGENT_TEMPERATURE == 0.0

    def test_agent_disabled_without_api_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        pkg = _reload_agent_module()
        assert pkg.DeepAgent().invoke("test")["enabled"] is False


# ---------------------------------------------------------------------------
# DeepAgent stub-mode tests (no API key)
# ---------------------------------------------------------------------------


class TestDeepAgentStub:
    """Verifies behaviour when OPENAI_API_KEY is absent."""

    def setup_method(self):
        os.environ.pop("OPENAI_API_KEY", None)

    def test_import(self):
        from app.agent import DeepAgent  # noqa: F401

    def test_instantiation_does_not_raise(self):
        from app.agent import DeepAgent

        agent = DeepAgent()
        assert agent is not None

    def test_invoke_returns_dict(self):
        from app.agent import DeepAgent

        result = DeepAgent().invoke("Olá agente")
        assert isinstance(result, dict)

    def test_invoke_has_required_keys(self):
        from app.agent import DeepAgent

        result = DeepAgent().invoke("test")
        assert "output" in result
        assert "model" in result
        assert "enabled" in result

    def test_invoke_stub_model(self):
        from app.agent import DeepAgent

        result = DeepAgent().invoke("test")
        assert result["model"] == "stub"
        assert result["enabled"] is False

    def test_invoke_stub_output_is_string(self):
        from app.agent import DeepAgent

        result = DeepAgent().invoke("qualquer pergunta")
        assert isinstance(result["output"], str)
        assert len(result["output"]) > 0


# ---------------------------------------------------------------------------
# DeepAgent enabled-mode tests (mocked LLM)
# ---------------------------------------------------------------------------


class TestDeepAgentEnabled:
    """Verifies behaviour when OPENAI_API_KEY is set and LLM is mocked."""

    def test_invoke_calls_chain(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-key")

        fake_response = MagicMock()
        fake_response.content = "Resposta do agente mockado."

        fake_chain = MagicMock()
        fake_chain.invoke.return_value = fake_response

        with patch("app.agent.base_agent.DeepAgent._build_chain", return_value=fake_chain):
            pkg = _reload_agent_module()
            agent = pkg.DeepAgent()
            agent._enabled = True
            agent._chain = fake_chain

            result = agent.invoke("Analise o template.")

        fake_chain.invoke.assert_called_once_with({"input": "Analise o template."})
        assert result["output"] == "Resposta do agente mockado."
        assert result["enabled"] is True

    def test_subclass_overrides_system_prompt(self):
        from app.agent import DeepAgent

        class MyAgent(DeepAgent):
            system_prompt = "Você é um agente customizado."

        agent = MyAgent()
        assert agent.system_prompt == "Você é um agente customizado."
        # Still degrades gracefully without API key
        result = agent.invoke("test")
        assert result["model"] == "stub"
