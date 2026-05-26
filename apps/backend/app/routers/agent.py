from fastapi import APIRouter

from app.services.deep_agent import DeepAgentStatus, get_deep_agent_status

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/status", response_model=DeepAgentStatus)
async def deep_agent_status() -> DeepAgentStatus:
    return get_deep_agent_status()
