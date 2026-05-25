from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import dumps_json, get_db, loads_json
from app.deps.session import require_session
from app.models import Character, Sheet, SheetRevision, Workspace
from app.routers.workspaces import template_image_url
from app.schemas import ExampleSheetResponse, SheetPatch, SheetRevisionResponse
from app.services.sheet_permissions import field_permissions
from app.services.sheet_validation import SheetValidationError, missing_required_fields, validate_sheet_data

router = APIRouter(prefix="/sheets", tags=["sheets"])


async def _get_sheet_or_404(db: AsyncSession, sheet_id: str) -> Sheet:
    result = await db.execute(
        select(Sheet)
        .options(selectinload(Sheet.character))
        .where(Sheet.id == sheet_id)
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Ficha não encontrada.")
    return sheet


async def _get_workspace_for_sheet(db: AsyncSession, sheet: Sheet) -> Workspace:
    result = await db.execute(select(Workspace).where(Workspace.id == sheet.workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace não encontrado.")
    return workspace


def _can_access_sheet(sheet: Sheet, role: str, email: str) -> bool:
    if role == "gm":
        return True
    return sheet.character.player_email.lower() == email.lower()


@router.get("/{sheet_id}", response_model=ExampleSheetResponse)
async def get_sheet(
    sheet_id: str,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> ExampleSheetResponse:
    role, email = session
    sheet = await _get_sheet_or_404(db, sheet_id)
    if not _can_access_sheet(sheet, role, email):
        raise HTTPException(status_code=403, detail="Sem permissão para ver esta ficha.")

    workspace = await _get_workspace_for_sheet(db, sheet)
    schema = loads_json(workspace.schema_json)
    canvas = loads_json(workspace.canvas_spec_json)
    data = loads_json(sheet.data_json)
    if not isinstance(schema, dict) or not isinstance(canvas, dict) or not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="Dados da ficha corrompidos.")

    perms = field_permissions(canvas, role, schema.get("fields", {}))
    missing = missing_required_fields(schema, data)

    return ExampleSheetResponse(
        label=f"{sheet.character.name} — ficha",
        schema_data=schema,  # type: ignore[arg-type]
        canvas_spec=canvas,  # type: ignore[arg-type]
        data=data,
        template_image_url=template_image_url(workspace.id, workspace.template_image_path),
        editable_fields=perms,
        role=role,
        revision=sheet.revision,
        updated_at=sheet.updated_at,
        missing_required=missing,
    )


@router.patch("/{sheet_id}", response_model=ExampleSheetResponse)
async def update_sheet(
    sheet_id: str,
    body: SheetPatch,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> ExampleSheetResponse:
    role, email = session
    sheet = await _get_sheet_or_404(db, sheet_id)
    if not _can_access_sheet(sheet, role, email):
        raise HTTPException(status_code=403, detail="Sem permissão para editar esta ficha.")

    workspace = await _get_workspace_for_sheet(db, sheet)
    if workspace.template_status != "published":
        raise HTTPException(status_code=400, detail="Template ainda não publicado.")

    schema = loads_json(workspace.schema_json)
    canvas = loads_json(workspace.canvas_spec_json)
    if not isinstance(schema, dict) or not isinstance(canvas, dict):
        raise HTTPException(status_code=500, detail="Schema inválido.")

    perms = field_permissions(canvas, role, schema.get("fields", {}))
    merged = {**loads_json(sheet.data_json), **body.data}  # type: ignore[dict-item]

    for key in body.data:
        if not perms.get(key, False):
            raise HTTPException(status_code=403, detail=f"Campo não editável: {key}")

    try:
        normalized = validate_sheet_data(schema, merged)
    except SheetValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors) from exc

    sheet.data_json = dumps_json(normalized)
    sheet.revision += 1
    sheet.updated_at = datetime.now(timezone.utc)
    sheet.template_version = workspace.template_version

    db.add(
        SheetRevision(
            sheet_id=sheet.id,
            data_json=sheet.data_json,
            revision=sheet.revision,
            source=f"{role}:{email}",
        )
    )
    await db.commit()
    await db.refresh(sheet)

    return await get_sheet(sheet_id, session, db)


@router.get("/{sheet_id}/revisions", response_model=list[SheetRevisionResponse])
async def list_revisions(
    sheet_id: str,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> list[SheetRevisionResponse]:
    role, email = session
    sheet = await _get_sheet_or_404(db, sheet_id)
    if not _can_access_sheet(sheet, role, email):
        raise HTTPException(status_code=403, detail="Sem permissão.")

    result = await db.execute(
        select(SheetRevision)
        .where(SheetRevision.sheet_id == sheet_id)
        .order_by(SheetRevision.created_at.desc())
        .limit(20)
    )
    return [
        SheetRevisionResponse(
            id=r.id,
            revision=r.revision,
            source=r.source,
            created_at=r.created_at,
            data=loads_json(r.data_json),  # type: ignore[arg-type]
        )
        for r in result.scalars().all()
    ]
