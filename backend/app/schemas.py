from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CampaignSummary(BaseModel):
    id: str
    name: str
    description: str
    version: str
    max_members: int
    template_image_url: str | None
    created_at: datetime


class CampaignDetail(CampaignSummary):
    invite_count: int
    pending_invites: int


class InviteCreate(BaseModel):
    email: EmailStr
    role: str = Field(default="player", pattern="^(player|gm)$")


class InviteResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    created_at: datetime


class ExampleSheetResponse(BaseModel):
    label: str
    schema_data: dict
    canvas_spec: dict
    data: dict
    template_image_url: str | None
