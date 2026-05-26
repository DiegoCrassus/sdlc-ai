"""Deep Agent package — public surface for SDLC-AI-Native agents.

Import example
--------------
    from app.agent import DeepAgent

    agent = DeepAgent()
    result = agent.invoke("Descreva as etapas do SDLC AI-Native.")
"""

from .base_agent import DeepAgent

__all__ = ["DeepAgent"]
