import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import dumps_json, get_db, loads_json
from app.fixtures.draft_placeholder import DRAFT_PLACEHOLDER_CANVAS, DRAFT_PLACEHOLDER_SCHEMA
from app.models import ExampleSheet, Workspace, WorkspaceInvite
from app.schemas import (
    ExampleSheetResponse,
    InviteCreate,
    InviteResponse,
    WorkspaceDetail,
    WorkspaceSummary,
)
from app.services.dpa_analyzer import analyze_template
from app.services.provisioning import provision_from_json
from app.services.template_storage import save_template_source

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

ALLOWED_IMAGE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
    "application/pdf",
}


def template_image_url(workspace_id: str, filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{settings.api_prefix}/workspaces/{workspace_id}/template-image"


def save_template_image(workspace_id: str, upload: UploadFile) -> tuple[str, str]:
    try:
        return save_template_source(workspace_id, upload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[WorkspaceSummary])
async def list_workspaces(db: AsyncSession = Depends(get_db)) -> list[WorkspaceSummary]:
    result = await db.execute(
        select(Workspace).order_by(Workspace.is_example.desc(), Workspace.created_at.desc())
    )
    return [_to_summary(w) for w in result.scalars().all()]


@router.post("", response_model=WorkspaceDetail, status_code=201)
async def create_workspace(
    name: str = Form(..., min_length=1, max_length=200),
    master_name: str = Form(..., min_length=1, max_length=200),
    description: str = Form(""),
    version: str = Form("1.0.0"),
    max_members: int = Form(4, ge=1, le=20),
    sheet_source: str = Form("file"),
    sheet_json: str = Form(""),
    sheet_text: str = Form(""),
    template_image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceDetail:
    if sheet_source not in {"file", "json", "text"}:
        raise HTTPException(status_code=400, detail="sheet_source deve ser file, json ou text.")

    workspace_id = str(uuid.uuid4())
    image_path: str | None = None
    source_mime: str | None = None
    input_raw: str | None = None
    template_status = "published"
    published_at = None
    analysis_json: str | None = None

    if sheet_source == "file":
        if not template_image or not template_image.filename:
            raise HTTPException(
                status_code=400,
                detail="Envie uma imagem da ficha (PNG, JPG ou WEBP) ou use JSON/texto.",
            )
        image_path, source_mime = save_template_image(workspace_id, template_image)
        schema, canvas, sheet_data = DRAFT_PLACEHOLDER_SCHEMA, DRAFT_PLACEHOLDER_CANVAS, {}
        template_status = "draft"
    elif sheet_source == "json":
        if not sheet_json.strip():
            raise HTTPException(status_code=400, detail="Informe o JSON da ficha.")
        input_raw = sheet_json.strip()
        schema, canvas, sheet_data = provision_from_json(input_raw)
        from datetime import datetime, timezone

        published_at = datetime.now(timezone.utc)
        result = analyze_template(sheet_source="json", sheet_input_raw=input_raw, has_image=False)
        analysis_json = dumps_json(result.model_dump())
    else:
        if not sheet_text.strip():
            raise HTTPException(status_code=400, detail="Descreva como é a ficha do seu RPG.")
        input_raw = sheet_text.strip()
        schema, canvas, sheet_data = DRAFT_PLACEHOLDER_SCHEMA, DRAFT_PLACEHOLDER_CANVAS, {}
        template_status = "draft"

    workspace = Workspace(
        id=workspace_id,
        name=name.strip(),
        description=description.strip(),
        master_name=master_name.strip(),
        version=version.strip(),
        max_members=max_members,
        sheet_source=sheet_source,
        sheet_input_raw=input_raw,
        template_image_path=image_path,
        source_mime=source_mime,
        schema_json=dumps_json(schema),
        canvas_spec_json=dumps_json(canvas),
        analysis_json=analysis_json,
        template_status=template_status,
        template_version=1,
        published_at=published_at,
        is_example=False,
    )
    workspace.example_sheet = ExampleSheet(
        workspace_id=workspace_id,
        data_json=dumps_json(sheet_data),
        label="Ficha exemplo — valores iniciais",
    )

    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    if template_status == "draft":
        result = analyze_template(
            sheet_source=workspace.sheet_source,
            sheet_input_raw=workspace.sheet_input_raw,
            has_image=bool(workspace.template_image_path),
        )
        workspace.analysis_json = dumps_json(result.model_dump())
        workspace.schema_json = dumps_json(result.sheet_schema)
        workspace.canvas_spec_json = dumps_json(result.canvas_spec)
        await db.commit()
        await db.refresh(workspace)

    return WorkspaceDetail(
        **_to_summary(workspace).model_dump(),
        invite_count=0,
        pending_invites=0,
    )


@router.get("/{workspace_id}", response_model=WorkspaceDetail)
async def get_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)) -> WorkspaceDetail:
    workspace = await _get_workspace_or_404(db, workspace_id)
    counts = await _invite_counts(db, workspace_id)
    return WorkspaceDetail(
        **_to_summary(workspace).model_dump(),
        invite_count=counts[0],
        pending_invites=counts[1],
    )


@router.get("/{workspace_id}/template-image")
async def get_template_image(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await _get_workspace_or_404(db, workspace_id)
    if not workspace.template_image_path:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")

    path = settings.upload_dir.parent / workspace.template_image_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo de imagem ausente.")

    return FileResponse(path)


@router.get("/{workspace_id}/invites", response_model=list[InviteResponse])
async def list_invites(
    workspace_id: str, db: AsyncSession = Depends(get_db)
) -> list[InviteResponse]:
    await _get_workspace_or_404(db, workspace_id)
    result = await db.execute(
        select(WorkspaceInvite)
        .where(WorkspaceInvite.workspace_id == workspace_id)
        .order_by(WorkspaceInvite.created_at.desc())
    )
    return [InviteResponse.model_validate(i, from_attributes=True) for i in result.scalars().all()]


@router.post("/{workspace_id}/invites", response_model=InviteResponse, status_code=201)
async def create_invite(
    workspace_id: str,
    body: InviteCreate,
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    workspace = await _get_workspace_or_404(db, workspace_id)

    existing = await db.execute(
        select(func.count())
        .select_from(WorkspaceInvite)
        .where(WorkspaceInvite.workspace_id == workspace_id)
    )
    if existing.scalar_one() >= workspace.max_members:
        raise HTTPException(status_code=400, detail="Limite de membros atingido.")

    duplicate = await db.execute(
        select(WorkspaceInvite).where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.email == body.email.lower(),
        )
    )
    if duplicate.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Este e-mail já foi convidado.")

    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        email=body.email.lower(),
        role=body.role,
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    return InviteResponse.model_validate(invite, from_attributes=True)


@router.get("/{workspace_id}/example-sheet", response_model=ExampleSheetResponse)
async def get_example_sheet(
    workspace_id: str, db: AsyncSession = Depends(get_db)
) -> ExampleSheetResponse:
    result = await db.execute(
        select(Workspace)
        .options(selectinload(Workspace.example_sheet))
        .where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if not workspace or not workspace.example_sheet:
        raise HTTPException(status_code=404, detail="Workspace ou ficha exemplo não encontrada.")

    return ExampleSheetResponse(
        label=workspace.example_sheet.label,
        schema_data=loads_json(workspace.schema_json),  # type: ignore[arg-type]
        canvas_spec=loads_json(workspace.canvas_spec_json),  # type: ignore[arg-type]
        data=loads_json(workspace.example_sheet.data_json),  # type: ignore[arg-type]
        template_image_url=template_image_url(workspace.id, workspace.template_image_path),
    )


async def _get_workspace_or_404(db: AsyncSession, workspace_id: str) -> Workspace:
    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado.")
    return workspace


async def _invite_counts(db: AsyncSession, workspace_id: str) -> tuple[int, int]:
    total = await db.execute(
        select(func.count())
        .select_from(WorkspaceInvite)
        .where(WorkspaceInvite.workspace_id == workspace_id)
    )
    pending = await db.execute(
        select(func.count())
        .select_from(WorkspaceInvite)
        .where(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.status == "pending",
        )
    )
    return total.scalar_one(), pending.scalar_one()


def _to_summary(workspace: Workspace) -> WorkspaceSummary:
    return WorkspaceSummary(
        id=workspace.id,
        name=workspace.name,
        description=workspace.description,
        master_name=workspace.master_name,
        version=workspace.version,
        max_members=workspace.max_members,
        sheet_source=workspace.sheet_source,
        template_status=workspace.template_status,
        template_version=workspace.template_version,
        is_example=workspace.is_example,
        template_image_url=template_image_url(workspace.id, workspace.template_image_path),
        created_at=workspace.created_at,
    )
