import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
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


class ExampleSheet(Base):
    __tablename__ = "example_sheets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("campaigns.id"), unique=True, nullable=False
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String(200), default="Ficha exemplo")

    campaign: Mapped["Campaign"] = relationship(back_populates="example_sheet")
