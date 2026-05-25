from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class WorkspaceSummary(BaseModel):
    id: str
    name: str
    description: str
    master_name: str
    version: str
    max_members: int
    sheet_source: str
    template_status: str
    template_version: int
    is_example: bool
    template_image_url: str | None
    created_at: datetime


class WorkspaceDetail(WorkspaceSummary):
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
    editable_fields: dict[str, bool] | None = None
    role: str | None = None
    revision: int | None = None
    updated_at: datetime | None = None
    missing_required: list[str] = Field(default_factory=list)


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    player_email: EmailStr


class CharacterSummary(BaseModel):
    id: str
    name: str
    player_email: str
    sheet_id: str | None
    revision: int | None
    updated_at: datetime | None
    missing_required: list[str] = Field(default_factory=list)
    incomplete: bool = False


class WorkspaceDashboard(BaseModel):
    workspace_id: str
    template_status: str
    template_version: int
    character_count: int
    incomplete_count: int
    characters: list[CharacterSummary]


class SheetPatch(BaseModel):
    data: dict


class SheetRevisionResponse(BaseModel):
    id: str
    revision: int
    source: str
    created_at: datetime
    data: dict
