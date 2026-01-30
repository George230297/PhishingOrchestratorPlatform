import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, Uuid, func, Enum as SAEnum
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import AttackVectorEnum, EventTypeEnum

class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    vector: Mapped[AttackVectorEnum] = mapped_column(SAEnum(AttackVectorEnum), nullable=False)
    subject_line: Mapped[Optional[str]] = mapped_column(String(255))
    html_content: Mapped[Optional[str]] = mapped_column(Text)
    landing_page_html: Mapped[Optional[str]] = mapped_column(Text)
    has_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    attachment_type: Mapped[Optional[str]] = mapped_column(String(10))

    # Relationships
    campaigns: Mapped[List["Campaign"]] = relationship(back_populates="template")

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id"))
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_anonymous_reporting: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="campaigns")
    template: Mapped["Template"] = relationship(back_populates="campaigns")
    dispatches: Mapped[List["CampaignDispatch"]] = relationship(back_populates="campaign")

class CampaignDispatch(Base):
    __tablename__ = "campaign_dispatches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    campaign_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campaigns.id"))
    target_id: Mapped[Optional[int]] = mapped_column(ForeignKey("targets.id"))
    sending_node_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sending_nodes.id"))
    used_domain_id: Mapped[Optional[int]] = mapped_column(ForeignKey("phishing_domains.id"))
    
    unique_tracking_token: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), server_default=func.gen_random_uuid(), index=True)
    dispatch_status: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="dispatches")
    target: Mapped["Target"] = relationship()
    sending_node: Mapped["SendingNode"] = relationship()
    used_domain: Mapped["PhishingDomain"] = relationship()
    events: Mapped[List["CampaignEvent"]] = relationship(back_populates="dispatch")
    credentials: Mapped[List["CapturedCredential"]] = relationship(back_populates="dispatch")

class CampaignEvent(Base):
    __tablename__ = "campaign_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    dispatch_id: Mapped[int] = mapped_column(ForeignKey("campaign_dispatches.id"))
    event_type: Mapped[EventTypeEnum] = mapped_column(SAEnum(EventTypeEnum), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(INET)
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    os_fingerprint: Mapped[Optional[str]] = mapped_column(String(100))
    browser_fingerprint: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dispatch: Mapped["CampaignDispatch"] = relationship(back_populates="events")

class CapturedCredential(Base):
    __tablename__ = "captured_credentials"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    dispatch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campaign_dispatches.id"))
    username_entered: Mapped[Optional[str]] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    was_password_leaked: Mapped[bool] = mapped_column(Boolean, default=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    dispatch: Mapped["CampaignDispatch"] = relationship(back_populates="credentials")
