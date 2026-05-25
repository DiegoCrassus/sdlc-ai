"""Dev session headers — simulates player/GM until real auth."""

from typing import Annotated

from fastapi import Header, HTTPException

SessionRole = Annotated[str, Header(alias="X-Session-Role", pattern="^(player|gm)$")]
SessionEmail = Annotated[str, Header(alias="X-Session-Email")]


def require_session(
    role: str = Header(default="gm", alias="X-Session-Role"),
    email: str = Header(default="mestre@local.dev", alias="X-Session-Email"),
) -> tuple[str, str]:
    if role not in {"player", "gm"}:
        raise HTTPException(status_code=400, detail="X-Session-Role deve ser player ou gm.")
    if not email.strip():
        raise HTTPException(status_code=400, detail="X-Session-Email obrigatório.")
    return role.strip().lower(), email.strip().lower()
