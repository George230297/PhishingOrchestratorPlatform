from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.enums import HealthStatusEnum

class SendingNode(Base):
    __tablename__ = "sending_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    smtp_host: Mapped[Optional[str]] = mapped_column(String(255))
    provider_id: Mapped[Optional[str]] = mapped_column(String(50))
    current_reputation: Mapped[int] = mapped_column(Integer, default=100)
    status: Mapped[HealthStatusEnum] = mapped_column(SAEnum(HealthStatusEnum), default=HealthStatusEnum.HEALTHY)
    daily_send_limit: Mapped[int] = mapped_column(Integer, default=500)
    current_daily_sends: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class PhishingDomain(Base):
    __tablename__ = "phishing_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_ssl_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[HealthStatusEnum] = mapped_column(SAEnum(HealthStatusEnum), default=HealthStatusEnum.HEALTHY)
