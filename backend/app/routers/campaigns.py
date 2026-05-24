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
from app.models import Campaign, CampaignInvite, ExampleSheet
from app.schemas import CampaignDetail, CampaignSummary, ExampleSheetResponse, InviteCreate, InviteResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}


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
async def list_invites(campaign_id: str, db: AsyncSession = Depends(get_db)) -> list[InviteResponse]:
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
async def get_example_sheet(campaign_id: str, db: AsyncSession = Depends(get_db)) -> ExampleSheetResponse:
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


async def _get_campaign_or_404(db: AsyncSession, campaign_id: str) -> Campaign:
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Sandbox RPG não encontrado.")
    return campaign


async def _invite_counts(db: AsyncSession, campaign_id: str) -> tuple[int, int]:
    total = await db.execute(
        select(func.count()).select_from(CampaignInvite).where(CampaignInvite.campaign_id == campaign_id)
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
