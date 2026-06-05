"""Auth routes: identify, me, logout."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.config import get_settings
from marketpulse.db.session import get_db_session
from marketpulse.deps import get_current_user
from marketpulse.domain.auth import (
    AuthMeResponse,
    CurrentUser,
    IdentifyRequest,
    IdentifyResponse,
    User,
)
from marketpulse.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/identify", response_model=IdentifyResponse)
async def identify(
    payload: IdentifyRequest,
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IdentifyResponse:
    settings = get_settings()
    prior_token = request.cookies.get(settings.session_cookie_name)
    user, token = await auth_service.identify_user(
        session,
        str(payload.email),
        prior_token=prior_token,
    )
    auth_service.set_session_cookie(response, token, settings)
    return IdentifyResponse(user=user)


@router.get("/me", response_model=AuthMeResponse)
async def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> AuthMeResponse:
    return AuthMeResponse(user=User(id=current_user.id, email=current_user.email))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def logout(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        await auth_service.delete_session_by_token(session, token)
    auth_service.clear_session_cookie(response, settings)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
