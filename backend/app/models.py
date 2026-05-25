import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    max_members: Mapped[int] = mapped_column(Integer, default=4)
    template_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    schema_json: Mapped[str] = mapped_column(Text, nullable=False)
    canvas_spec_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    invites: Mapped[list["CampaignInvite"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    members: Mapped[list["CampaignMember"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    templates: Mapped[list["SheetTemplate"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    characters: Mapped[list["Character"]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )
    example_sheet: Mapped["ExampleSheet | None"] = relationship(
        back_populates="campaign", uselist=False, cascade="all, delete-orphan"
    )


class CampaignInvite(Base):
    __tablename__ = "campaign_invites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="player")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    campaign: Mapped["Campaign"] = relationship(back_populates="invites")


class CampaignMember(Base):
    __tablename__ = "campaign_members"
    __table_args__ = (UniqueConstraint("campaign_id", "email", name="uq_campaign_member_email"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[str] = mapped_column(String(20), default="player")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    campaign: Mapped["Campaign"] = relationship(back_populates="members")
    characters: Mapped[list["Character"]] = relationship(back_populates="owner")


class SheetTemplate(Base):
    __tablename__ = "sheet_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), default="Template base")
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="published")
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    analysis_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema_json: Mapped[str] = mapped_column(Text, nullable=False)
    canvas_spec_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="templates")
    sheets: Mapped[list["Sheet"]] = relationship(back_populates="template")


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    owner_member_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("campaign_members.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    campaign: Mapped["Campaign"] = relationship(back_populates="characters")
    owner: Mapped["CampaignMember | None"] = relationship(back_populates="characters")
    sheets: Mapped[list["Sheet"]] = relationship(back_populates="character")


class Sheet(Base):
    __tablename__ = "sheets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    character_id: Mapped[str] = mapped_column(String(36), ForeignKey("characters.id"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(36), ForeignKey("sheet_templates.id"), nullable=False)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String(200), default="Ficha")
    revision: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    character: Mapped["Character"] = relationship(back_populates="sheets")
    template: Mapped["SheetTemplate"] = relationship(back_populates="sheets")
    revisions: Mapped[list["SheetRevision"]] = relationship(
        back_populates="sheet", cascade="all, delete-orphan"
    )


class SheetRevision(Base):
    __tablename__ = "sheet_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sheet_id: Mapped[str] = mapped_column(String(36), ForeignKey("sheets.id"), nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    sheet: Mapped["Sheet"] = relationship(back_populates="revisions")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), default="template_source")
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ExampleSheet(Base):
    __tablename__ = "example_sheets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id"), unique=True, nullable=False
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String(200), default="Ficha exemplo")

    campaign: Mapped["Campaign"] = relationship(back_populates="example_sheet")
