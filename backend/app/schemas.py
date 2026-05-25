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


class SheetTemplateResponse(BaseModel):
    id: str
    name: str
    version: int
    status: str
    schema_data: dict
    canvas_spec: dict
    analysis: dict | None = None
    published_at: datetime | None = None


class CharacterResponse(BaseModel):
    id: str
    name: str
    owner_email: str | None = None


class SheetSummary(BaseModel):
    id: str
    label: str
    character: CharacterResponse
    template_version: int
    revision: int
    updated_at: datetime
    incomplete_fields: list[str] = []


class SheetDetail(BaseModel):
    id: str
    label: str
    character: CharacterResponse
    schema_data: dict
    canvas_spec: dict
    data: dict
    template_version: int
    revision: int
    template_image_url: str | None


class CampaignSheetsResponse(BaseModel):
    campaign: CampaignDetail
    sheets: list[SheetSummary]


class SheetUpdate(BaseModel):
    data: dict


class SheetRevisionResponse(BaseModel):
    id: str
    revision: int
    data: dict
    created_at: datetime


class PublishTemplateRequest(BaseModel):
    confirm: bool = False


class ExtendTemplateRequest(BaseModel):
    section_title: str
    field_key: str
    field_label: str
    field_type: str = Field(default="string", pattern="^(string|integer|float|boolean|text)$")
    default: str | int | float | bool | None = None


class TemplateAnalysisResponse(BaseModel):
    template: SheetTemplateResponse
    warnings: list[str] = []
