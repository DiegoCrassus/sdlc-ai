"""Auth domain models (auth.schema.json)."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, field_validator

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _validate_email_format(value: str) -> str:
    normalized = value.strip()
    if not _EMAIL_RE.match(normalized):
        raise ValueError("Invalid email format")
    return normalized


class User(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    email: str


class IdentifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return _validate_email_format(value)


class IdentifyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: User


class AuthMeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: User


class CurrentUser(BaseModel):
    """Authenticated user resolved from session cookie."""

    model_config = ConfigDict(frozen=True)

    id: str
    email: str
