import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import dumps_json, get_db, loads_json
from app.fixtures.default_template import DEFAULT_CANVAS_SPEC, DEFAULT_SCHEMA, MOCK_SHEET_DATA
from app.models import (
    Attachment,
    Campaign,
    CampaignInvite,
    CampaignMember,
    Character,
    ExampleSheet,
    Sheet,
    SheetRevision,
    SheetTemplate,
    utcnow,
)
from app.schemas import (
    CampaignDetail,
    CampaignSheetsResponse,
    CampaignSummary,
    CharacterResponse,
    ExampleSheetResponse,
    ExtendTemplateRequest,
    InviteCreate,
    InviteResponse,
    PublishTemplateRequest,
    SheetDetail,
    SheetRevisionResponse,
    SheetSummary,
    SheetTemplateResponse,
    SheetUpdate,
    TemplateAnalysisResponse,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
sheets_router = APIRouter(prefix="/sheets", tags=["sheets"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}
ALLOWED_TEMPLATE_SOURCE_TYPES = ALLOWED_IMAGE_TYPES | {"application/pdf"}


def template_image_url(campaign_id: str, filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{settings.api_prefix}/campaigns/{campaign_id}/template-image"


def save_template_image(campaign_id: str, upload: UploadFile) -> str:
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Formato inválido. Use PNG, JPG ou WEBP.")

    ext = Path(upload.filename or "template.png").suffix.lower() or ".png"
    dest_dir = settings.upload_dir / campaign_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"template{ext}"
    dest_path = dest_dir / filename

    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    return str(dest_path.relative_to(settings.upload_dir.parent))


def save_template_source(campaign_id: str, upload: UploadFile) -> str:
    if upload.content_type not in ALLOWED_TEMPLATE_SOURCE_TYPES:
        raise HTTPException(status_code=400, detail="Formato inválido. Use PDF, PNG ou JPG.")

    ext = Path(upload.filename or "template-source").suffix.lower() or ".bin"
    dest_dir = settings.upload_dir / campaign_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"template-source{ext}"
    dest_path = dest_dir / filename
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return str(dest_path.relative_to(settings.upload_dir.parent))


@router.get("", response_model=list[CampaignSummary])
async def list_campaigns(db: AsyncSession = Depends(get_db)) -> list[CampaignSummary]:
    result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
    campaigns = result.scalars().all()
    return [
        CampaignSummary(
            id=c.id,
            name=c.name,
            description=c.description,
            version=c.version,
            max_members=c.max_members,
            template_image_url=template_image_url(c.id, c.template_image_path),
            created_at=c.created_at,
        )
        for c in campaigns
    ]


@router.post("", response_model=CampaignDetail, status_code=201)
async def create_campaign(
    name: str = Form(..., min_length=1, max_length=200),
    description: str = Form(""),
    version: str = Form("1.0.0"),
    max_members: int = Form(4, ge=1, le=20),
    template_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> CampaignDetail:
    campaign_id = str(uuid.uuid4())
    image_path = save_template_image(campaign_id, template_image)

    campaign = Campaign(
        id=campaign_id,
        name=name.strip(),
        description=description.strip(),
        version=version.strip(),
        max_members=max_members,
        template_image_path=image_path,
        schema_json=dumps_json(DEFAULT_SCHEMA),
        canvas_spec_json=dumps_json(DEFAULT_CANVAS_SPEC),
    )
    example = ExampleSheet(
        campaign_id=campaign_id,
        data_json=dumps_json(MOCK_SHEET_DATA),
        label="Ficha exemplo — valores mockados",
    )
    campaign.example_sheet = example
    gm = CampaignMember(
        campaign_id=campaign_id,
        email="gm@example.local",
        display_name="Mestre",
        role="gm",
    )
    template = SheetTemplate(
        campaign_id=campaign_id,
        name="Template base",
        version=1,
        status="published",
        source_path=image_path,
        schema_json=dumps_json(DEFAULT_SCHEMA),
        canvas_spec_json=dumps_json(DEFAULT_CANVAS_SPEC),
        analysis_json=dumps_json(_analysis_for(DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC)),
        published_at=utcnow(),
    )
    character = Character(
        campaign_id=campaign_id,
        owner=gm,
        name=str(MOCK_SHEET_DATA["character_name"]),
    )
    sheet = Sheet(
        campaign_id=campaign_id,
        character=character,
        template=template,
        data_json=dumps_json(MOCK_SHEET_DATA),
        label="Ficha exemplo — valores mockados",
    )
    sheet.revisions.append(SheetRevision(revision=1, data_json=dumps_json(MOCK_SHEET_DATA)))
    db.add_all([gm, template, character, sheet])

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return CampaignDetail(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        version=campaign.version,
        max_members=campaign.max_members,
        template_image_url=template_image_url(campaign.id, campaign.template_image_path),
        created_at=campaign.created_at,
        invite_count=0,
        pending_invites=0,
    )


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)) -> CampaignDetail:
    campaign = await _get_campaign_or_404(db, campaign_id)
    counts = await _invite_counts(db, campaign_id)
    return _to_detail(campaign, counts)


@router.get("/{campaign_id}/template-image")
async def get_template_image(campaign_id: str, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse

    campaign = await _get_campaign_or_404(db, campaign_id)
    if not campaign.template_image_path:
        raise HTTPException(status_code=404, detail="Imagem não encontrada.")

    path = settings.upload_dir.parent / campaign.template_image_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo de imagem ausente.")

    return FileResponse(path)


@router.get("/{campaign_id}/invites", response_model=list[InviteResponse])
async def list_invites(
    campaign_id: str, db: AsyncSession = Depends(get_db)
) -> list[InviteResponse]:
    await _get_campaign_or_404(db, campaign_id)
    result = await db.execute(
        select(CampaignInvite)
        .where(CampaignInvite.campaign_id == campaign_id)
        .order_by(CampaignInvite.created_at.desc())
    )
    return [InviteResponse.model_validate(i, from_attributes=True) for i in result.scalars().all()]


@router.post("/{campaign_id}/invites", response_model=InviteResponse, status_code=201)
async def create_invite(
    campaign_id: str,
    body: InviteCreate,
    db: AsyncSession = Depends(get_db),
) -> InviteResponse:
    campaign = await _get_campaign_or_404(db, campaign_id)

    existing = await db.execute(
        select(func.count())
        .select_from(CampaignInvite)
        .where(CampaignInvite.campaign_id == campaign_id)
    )
    if existing.scalar_one() >= campaign.max_members:
        raise HTTPException(status_code=400, detail="Limite de membros atingido.")

    duplicate = await db.execute(
        select(CampaignInvite).where(
            CampaignInvite.campaign_id == campaign_id,
            CampaignInvite.email == body.email.lower(),
        )
    )
    if duplicate.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Este e-mail já foi convidado.")

    invite = CampaignInvite(
        campaign_id=campaign_id,
        email=body.email.lower(),
        role=body.role,
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    return InviteResponse.model_validate(invite, from_attributes=True)


@router.get("/{campaign_id}/example-sheet", response_model=ExampleSheetResponse)
async def get_example_sheet(
    campaign_id: str, db: AsyncSession = Depends(get_db)
) -> ExampleSheetResponse:
    result = await db.execute(
        select(Campaign)
        .options(selectinload(Campaign.example_sheet))
        .where(Campaign.id == campaign_id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign or not campaign.example_sheet:
        raise HTTPException(status_code=404, detail="Campanha ou ficha exemplo não encontrada.")

    return ExampleSheetResponse(
        label=campaign.example_sheet.label,
        schema_data=loads_json(campaign.schema_json),  # type: ignore[arg-type]
        canvas_spec=loads_json(campaign.canvas_spec_json),  # type: ignore[arg-type]
        data=loads_json(campaign.example_sheet.data_json),  # type: ignore[arg-type]
        template_image_url=template_image_url(campaign.id, campaign.template_image_path),
    )


@router.get("/{campaign_id}/sheets", response_model=CampaignSheetsResponse)
async def list_campaign_sheets(
    campaign_id: str, db: AsyncSession = Depends(get_db)
) -> CampaignSheetsResponse:
    campaign = await _get_campaign_or_404(db, campaign_id)
    result = await db.execute(
        select(Sheet)
        .options(
            selectinload(Sheet.character).selectinload(Character.owner),
            selectinload(Sheet.template),
        )
        .where(Sheet.campaign_id == campaign_id)
        .order_by(Sheet.updated_at.desc())
    )
    counts = await _invite_counts(db, campaign_id)
    sheets = [_to_sheet_summary(sheet) for sheet in result.scalars().all()]
    return CampaignSheetsResponse(campaign=_to_detail(campaign, counts), sheets=sheets)


@router.get("/{campaign_id}/template", response_model=SheetTemplateResponse)
async def get_published_template(
    campaign_id: str, db: AsyncSession = Depends(get_db)
) -> SheetTemplateResponse:
    template = await _latest_template_or_404(db, campaign_id)
    return _to_template_response(template)


@router.post("/{campaign_id}/template/source", response_model=TemplateAnalysisResponse)
async def upload_template_source(
    campaign_id: str,
    template_source: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> TemplateAnalysisResponse:
    campaign = await _get_campaign_or_404(db, campaign_id)
    source_path = save_template_source(campaign_id, template_source)
    analysis = _analysis_for(DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC)
    template = SheetTemplate(
        campaign_id=campaign_id,
        name="Template draft analisado",
        version=await _next_template_version(db, campaign_id),
        status="draft",
        source_path=source_path,
        schema_json=dumps_json(DEFAULT_SCHEMA),
        canvas_spec_json=dumps_json(DEFAULT_CANVAS_SPEC),
        analysis_json=dumps_json(analysis),
    )
    campaign.template_image_path = source_path if template_source.content_type in ALLOWED_IMAGE_TYPES else campaign.template_image_path
    db.add(template)
    db.add(
        Attachment(
            campaign_id=campaign_id,
            kind="template_source",
            path=source_path,
            content_type=template_source.content_type or "application/octet-stream",
        )
    )
    await db.commit()
    await db.refresh(template)
    return TemplateAnalysisResponse(
        template=_to_template_response(template),
        warnings=list(analysis["warnings"]),
    )


@router.post("/{campaign_id}/template/publish", response_model=SheetTemplateResponse)
async def publish_template(
    campaign_id: str,
    body: PublishTemplateRequest,
    db: AsyncSession = Depends(get_db),
) -> SheetTemplateResponse:
    if not body.confirm:
        raise HTTPException(status_code=400, detail="Confirmação humana obrigatória para publicar.")
    template = await _latest_template_or_404(db, campaign_id, include_draft=True)
    template.status = "published"
    template.published_at = utcnow()
    await db.commit()
    await db.refresh(template)
    return _to_template_response(template)


@router.post("/{campaign_id}/template/extend", response_model=SheetTemplateResponse)
async def extend_template(
    campaign_id: str,
    body: ExtendTemplateRequest,
    db: AsyncSession = Depends(get_db),
) -> SheetTemplateResponse:
    current = await _latest_template_or_404(db, campaign_id)
    schema = loads_json(current.schema_json)
    canvas = loads_json(current.canvas_spec_json)
    if not isinstance(schema, dict) or not isinstance(canvas, dict):
        raise HTTPException(status_code=500, detail="Template inválido.")
    fields = schema.setdefault("fields", {})
    if body.field_key in fields:
        raise HTTPException(status_code=409, detail="Campo já existe no template.")

    fields[body.field_key] = {"type": body.field_type, "label": body.field_label}
    regions = canvas.setdefault("regions", [])
    regions.append(
        {
            "id": body.field_key,
            "title": body.section_title,
            "order": len(regions),
            "presentation": "rich_text" if body.field_type == "text" else "field_grid",
            "fields": [body.field_key],
            "columns": 1,
        }
    )
    next_version = await _next_template_version(db, campaign_id)
    template = SheetTemplate(
        campaign_id=campaign_id,
        name=f"{current.name} v{next_version}",
        version=next_version,
        status="published",
        source_path=current.source_path,
        schema_json=dumps_json(schema),
        canvas_spec_json=dumps_json(canvas),
        analysis_json=dumps_json(
            {
                "mode": "extend",
                "added_fields": [body.field_key],
                "warnings": ["Extensão append-only aplicada ao template."],
            }
        ),
        published_at=utcnow(),
    )
    db.add(template)
    await db.flush()
    await _apply_template_defaults(db, campaign_id, template.id, body.field_key, body.default)
    await db.commit()
    await db.refresh(template)
    return _to_template_response(template)


@sheets_router.get("/{sheet_id}", response_model=SheetDetail)
@router.get("/sheets/{sheet_id}", response_model=SheetDetail)
async def get_sheet(sheet_id: str, db: AsyncSession = Depends(get_db)) -> SheetDetail:
    sheet = await _get_sheet_or_404(db, sheet_id)
    return _to_sheet_detail(sheet)


@sheets_router.put("/{sheet_id}", response_model=SheetDetail)
@router.put("/sheets/{sheet_id}", response_model=SheetDetail)
async def update_sheet(sheet_id: str, body: SheetUpdate, db: AsyncSession = Depends(get_db)) -> SheetDetail:
    sheet = await _get_sheet_or_404(db, sheet_id)
    schema = loads_json(sheet.template.schema_json)
    if not isinstance(schema, dict):
        raise HTTPException(status_code=500, detail="Schema do template inválido.")
    merged = loads_json(sheet.data_json)
    if not isinstance(merged, dict):
        merged = {}
    merged.update(body.data)
    errors = _validate_sheet_data(merged, schema)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    sheet.revision += 1
    sheet.updated_at = utcnow()
    sheet.data_json = dumps_json(merged)
    sheet.revisions.append(SheetRevision(revision=sheet.revision, data_json=dumps_json(merged)))
    await db.commit()
    await db.refresh(sheet)
    return _to_sheet_detail(sheet)


@sheets_router.get("/{sheet_id}/revisions", response_model=list[SheetRevisionResponse])
@router.get("/sheets/{sheet_id}/revisions", response_model=list[SheetRevisionResponse])
async def list_sheet_revisions(
    sheet_id: str, db: AsyncSession = Depends(get_db)
) -> list[SheetRevisionResponse]:
    await _get_sheet_or_404(db, sheet_id)
    result = await db.execute(
        select(SheetRevision).where(SheetRevision.sheet_id == sheet_id).order_by(SheetRevision.revision)
    )
    return [
        SheetRevisionResponse(
            id=rev.id,
            revision=rev.revision,
            data=loads_json(rev.data_json),  # type: ignore[arg-type]
            created_at=rev.created_at,
        )
        for rev in result.scalars().all()
    ]


async def _get_campaign_or_404(db: AsyncSession, campaign_id: str) -> Campaign:
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Sandbox RPG não encontrado.")
    return campaign


async def _latest_template_or_404(
    db: AsyncSession, campaign_id: str, *, include_draft: bool = False
) -> SheetTemplate:
    query = select(SheetTemplate).where(SheetTemplate.campaign_id == campaign_id)
    if not include_draft:
        query = query.where(SheetTemplate.status == "published")
    result = await db.execute(query.order_by(SheetTemplate.version.desc()))
    template = result.scalars().first()
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado.")
    return template


async def _next_template_version(db: AsyncSession, campaign_id: str) -> int:
    result = await db.execute(
        select(func.max(SheetTemplate.version)).where(SheetTemplate.campaign_id == campaign_id)
    )
    return int(result.scalar_one() or 0) + 1


async def _get_sheet_or_404(db: AsyncSession, sheet_id: str) -> Sheet:
    result = await db.execute(
        select(Sheet)
        .options(
            selectinload(Sheet.character).selectinload(Character.owner),
            selectinload(Sheet.template),
            selectinload(Sheet.revisions),
        )
        .where(Sheet.id == sheet_id)
    )
    sheet = result.scalar_one_or_none()
    if not sheet:
        raise HTTPException(status_code=404, detail="Ficha não encontrada.")
    return sheet


async def _invite_counts(db: AsyncSession, campaign_id: str) -> tuple[int, int]:
    total = await db.execute(
        select(func.count())
        .select_from(CampaignInvite)
        .where(CampaignInvite.campaign_id == campaign_id)
    )
    pending = await db.execute(
        select(func.count())
        .select_from(CampaignInvite)
        .where(CampaignInvite.campaign_id == campaign_id, CampaignInvite.status == "pending")
    )
    return total.scalar_one(), pending.scalar_one()


def _to_detail(campaign: Campaign, counts: tuple[int, int]) -> CampaignDetail:
    return CampaignDetail(
        id=campaign.id,
        name=campaign.name,
        description=campaign.description,
        version=campaign.version,
        max_members=campaign.max_members,
        template_image_url=template_image_url(campaign.id, campaign.template_image_path),
        created_at=campaign.created_at,
        invite_count=counts[0],
        pending_invites=counts[1],
    )


def _to_template_response(template: SheetTemplate) -> SheetTemplateResponse:
    return SheetTemplateResponse(
        id=template.id,
        name=template.name,
        version=template.version,
        status=template.status,
        schema_data=loads_json(template.schema_json),  # type: ignore[arg-type]
        canvas_spec=loads_json(template.canvas_spec_json),  # type: ignore[arg-type]
        analysis=loads_json(template.analysis_json) if template.analysis_json else None,  # type: ignore[arg-type]
        published_at=template.published_at,
    )


def _to_character_response(character: Character) -> CharacterResponse:
    return CharacterResponse(
        id=character.id,
        name=character.name,
        owner_email=character.owner.email if character.owner else None,
    )


def _to_sheet_summary(sheet: Sheet) -> SheetSummary:
    schema = loads_json(sheet.template.schema_json)
    data = loads_json(sheet.data_json)
    incomplete = _incomplete_fields(data, schema) if isinstance(data, dict) and isinstance(schema, dict) else []
    return SheetSummary(
        id=sheet.id,
        label=sheet.label,
        character=_to_character_response(sheet.character),
        template_version=sheet.template.version,
        revision=sheet.revision,
        updated_at=sheet.updated_at,
        incomplete_fields=incomplete,
    )


def _to_sheet_detail(sheet: Sheet) -> SheetDetail:
    return SheetDetail(
        id=sheet.id,
        label=sheet.label,
        character=_to_character_response(sheet.character),
        schema_data=loads_json(sheet.template.schema_json),  # type: ignore[arg-type]
        canvas_spec=loads_json(sheet.template.canvas_spec_json),  # type: ignore[arg-type]
        data=loads_json(sheet.data_json),  # type: ignore[arg-type]
        template_version=sheet.template.version,
        revision=sheet.revision,
        template_image_url=template_image_url(sheet.campaign_id, sheet.template.source_path),
    )


def _analysis_for(schema: dict, canvas: dict) -> dict:
    return {
        "mode": "fixture",
        "steps": [
            {"name": "segment_regions", "status": "ok", "regions": len(canvas.get("regions", []))},
            {"name": "list_fields", "status": "ok", "fields": len(schema.get("fields", {}))},
            {"name": "infer_types", "status": "ok"},
            {"name": "build_canvas", "status": "ok"},
        ],
        "warnings": ["Análise determinística MVP; revisar antes de publicar templates reais."],
    }


def _validate_sheet_data(data: dict, schema: dict) -> list[str]:
    fields = schema.get("fields", {})
    errors: list[str] = []
    if not isinstance(fields, dict):
        return ["Schema de campos inválido."]
    for key, field in fields.items():
        if not isinstance(field, dict):
            continue
        value = data.get(key)
        if field.get("required") and value in (None, ""):
            errors.append(f"{key}: campo obrigatório.")
            continue
        if value in (None, ""):
            continue
        field_type = field.get("type")
        if field_type == "integer":
            if not isinstance(value, int):
                errors.append(f"{key}: esperado integer.")
                continue
            if field.get("min") is not None and value < int(field["min"]):
                errors.append(f"{key}: abaixo do mínimo.")
            if field.get("max") is not None and value > int(field["max"]):
                errors.append(f"{key}: acima do máximo.")
        elif field_type in {"string", "text"} and not isinstance(value, str):
            errors.append(f"{key}: esperado texto.")
    return errors


def _incomplete_fields(data: dict, schema: dict) -> list[str]:
    fields = schema.get("fields", {})
    if not isinstance(fields, dict):
        return []
    return [
        key
        for key, field in fields.items()
        if isinstance(field, dict) and field.get("required") and data.get(key) in (None, "")
    ]


async def _apply_template_defaults(
    db: AsyncSession, campaign_id: str, template_id: str, field_key: str, default: object
) -> None:
    result = await db.execute(select(Sheet).where(Sheet.campaign_id == campaign_id))
    for sheet in result.scalars().all():
        data = loads_json(sheet.data_json)
        if not isinstance(data, dict):
            data = {}
        data.setdefault(field_key, default if default is not None else "")
        sheet.template_id = template_id
        sheet.revision += 1
        sheet.updated_at = utcnow()
        sheet.data_json = dumps_json(data)
        db.add(SheetRevision(sheet_id=sheet.id, revision=sheet.revision, data_json=dumps_json(data)))
