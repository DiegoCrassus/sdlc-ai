import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import dumps_json, get_db, loads_json
from app.deps.session import require_session
from app.models import Character, Sheet, Workspace
from app.routers.workspaces import _get_workspace_or_404, template_image_url
from app.schemas import CharacterCreate, CharacterSummary, WorkspaceDashboard
from app.services.provisioning import empty_defaults
from app.services.sheet_validation import missing_required_fields

router = APIRouter(prefix="/workspaces", tags=["characters"])


@router.get("/{workspace_id}/dashboard", response_model=WorkspaceDashboard)
async def get_workspace_dashboard(
    workspace_id: str,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceDashboard:
    role, _email = session
    if role != "gm":
        raise HTTPException(status_code=403, detail="Dashboard disponível apenas para o mestre.")

    workspace = await _get_workspace_or_404(db, workspace_id)
    schema = loads_json(workspace.schema_json)
    if not isinstance(schema, dict):
        schema = {"fields": {}}

    result = await db.execute(
        select(Character)
        .options(selectinload(Character.sheet))
        .where(Character.workspace_id == workspace_id)
        .order_by(Character.name)
    )
    characters = result.scalars().all()
    summaries: list[CharacterSummary] = []
    incomplete_count = 0

    for char in characters:
        missing: list[str] = []
        if char.sheet:
            data = loads_json(char.sheet.data_json)
            if isinstance(data, dict):
                missing = missing_required_fields(schema, data)
        incomplete = len(missing) > 0
        if incomplete:
            incomplete_count += 1
        summaries.append(
            CharacterSummary(
                id=char.id,
                name=char.name,
                player_email=char.player_email,
                sheet_id=char.sheet.id if char.sheet else None,
                revision=char.sheet.revision if char.sheet else None,
                updated_at=char.sheet.updated_at if char.sheet else None,
                missing_required=missing,
                incomplete=incomplete,
            )
        )

    return WorkspaceDashboard(
        workspace_id=workspace.id,
        template_status=workspace.template_status,
        template_version=workspace.template_version,
        character_count=len(summaries),
        incomplete_count=incomplete_count,
        characters=summaries,
    )


@router.get("/{workspace_id}/characters", response_model=list[CharacterSummary])
async def list_characters(
    workspace_id: str,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> list[CharacterSummary]:
    role, email = session
    workspace = await _get_workspace_or_404(db, workspace_id)
    schema = loads_json(workspace.schema_json)

    query = (
        select(Character)
        .options(selectinload(Character.sheet))
        .where(Character.workspace_id == workspace_id)
        .order_by(Character.name)
    )
    if role == "player":
        query = query.where(Character.player_email == email)

    result = await db.execute(query)
    chars = result.scalars().all()
    out: list[CharacterSummary] = []
    for char in chars:
        missing: list[str] = []
        if char.sheet and isinstance(schema, dict):
            data = loads_json(char.sheet.data_json)
            if isinstance(data, dict):
                missing = missing_required_fields(schema, data)
        out.append(
            CharacterSummary(
                id=char.id,
                name=char.name,
                player_email=char.player_email,
                sheet_id=char.sheet.id if char.sheet else None,
                revision=char.sheet.revision if char.sheet else None,
                updated_at=char.sheet.updated_at if char.sheet else None,
                missing_required=missing,
                incomplete=len(missing) > 0,
            )
        )
    return out


@router.post("/{workspace_id}/characters", response_model=CharacterSummary, status_code=201)
async def create_character(
    workspace_id: str,
    body: CharacterCreate,
    session: tuple[str, str] = Depends(require_session),
    db: AsyncSession = Depends(get_db),
) -> CharacterSummary:
    role, _email = session
    if role != "gm":
        raise HTTPException(status_code=403, detail="Apenas o mestre pode criar personagens.")

    workspace = await _get_workspace_or_404(db, workspace_id)
    if workspace.template_status != "published":
        raise HTTPException(status_code=400, detail="Publique o template antes de criar personagens.")

    schema = loads_json(workspace.schema_json)
    if not isinstance(schema, dict):
        raise HTTPException(status_code=500, detail="Schema do workspace inválido.")

    char_id = str(uuid.uuid4())
    sheet_id = str(uuid.uuid4())
    defaults = empty_defaults(schema)
    defaults["character_name"] = body.name
    defaults["player_name"] = body.player_email.split("@")[0]

    character = Character(
        id=char_id,
        workspace_id=workspace_id,
        name=body.name.strip(),
        player_email=body.player_email.lower(),
    )
    character.sheet = Sheet(
        id=sheet_id,
        workspace_id=workspace_id,
        character_id=char_id,
        template_version=workspace.template_version,
        data_json=dumps_json(defaults),
        revision=1,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(character)
    await db.commit()
    await db.refresh(character)
    await db.refresh(character.sheet)

    missing = missing_required_fields(schema, defaults)
    return CharacterSummary(
        id=character.id,
        name=character.name,
        player_email=character.player_email,
        sheet_id=character.sheet.id,
        revision=character.sheet.revision,
        updated_at=character.sheet.updated_at,
        missing_required=missing,
        incomplete=len(missing) > 0,
    )
