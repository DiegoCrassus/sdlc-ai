"""Email session auth: users, sessions, cookie helpers."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.config import Settings, get_settings
from marketpulse.db.models import SessionRow, UserRow
from marketpulse.domain.auth import CurrentUser, User

def normalize_email(email: str) -> str:
    return email.strip().lower()


def set_session_cookie(response: Response, token: str, settings: Settings | None = None) -> None:
    resolved = settings or get_settings()
    response.set_cookie(
        key=resolved.session_cookie_name,
        value=token,
        max_age=resolved.session_ttl_seconds,
        httponly=True,
        samesite="lax",
        path="/",
        secure=resolved.session_cookie_secure,
    )


def clear_session_cookie(response: Response, settings: Settings | None = None) -> None:
    resolved = settings or get_settings()
    response.delete_cookie(
        key=resolved.session_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
        secure=resolved.session_cookie_secure,
    )


def _user_from_row(row: UserRow) -> User:
    return User(id=row.id, email=row.email)


async def upsert_user(session: AsyncSession, email: str) -> UserRow:
    normalized = normalize_email(email)
    result = await session.execute(select(UserRow).where(UserRow.email == normalized))
    row = result.scalar_one_or_none()
    if row is not None:
        return row
    now = datetime.now(tz=UTC)
    row = UserRow(id=str(uuid.uuid4()), email=normalized, created_at=now)
    session.add(row)
    await session.flush()
    return row


async def create_session(session: AsyncSession, user_id: str) -> str:
    settings = get_settings()
    token = secrets.token_urlsafe(32)
    now = datetime.now(tz=UTC)
    expires_at = now + timedelta(seconds=settings.session_ttl_seconds)
    session.add(
        SessionRow(
            id=token,
            user_id=user_id,
            expires_at=expires_at,
            created_at=now,
        )
    )
    await session.flush()
    return token


async def delete_session_by_token(session: AsyncSession, token: str) -> None:
    await session.execute(delete(SessionRow).where(SessionRow.id == token))
    await session.flush()


async def resolve_session(session: AsyncSession, token: str) -> CurrentUser | None:
    now = datetime.now(tz=UTC)
    stmt = (
        select(UserRow)
        .join(SessionRow, SessionRow.user_id == UserRow.id)
        .where(SessionRow.id == token, SessionRow.expires_at > now)
    )
    result = await session.execute(stmt)
    user_row = result.scalar_one_or_none()
    if user_row is None:
        return None
    return CurrentUser(id=user_row.id, email=user_row.email)


async def identify_user(
    session: AsyncSession,
    email: str,
    *,
    prior_token: str | None = None,
) -> tuple[User, str]:
    """Upsert user, rotate session, return user + new token."""
    if prior_token:
        await delete_session_by_token(session, prior_token)
    user_row = await upsert_user(session, email)
    token = await create_session(session, user_row.id)
    return _user_from_row(user_row), token
