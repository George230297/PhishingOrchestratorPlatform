from typing import List, Optional
from datetime import datetime
from app.models.enums import SubscriptionPlanEnum
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_plan: Mapped[SubscriptionPlanEnum] = mapped_column(SAEnum(SubscriptionPlanEnum), default=SubscriptionPlanEnum.FREE)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    departments: Mapped[List["Department"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    targets: Mapped[List["Target"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    campaigns: Mapped[List["Campaign"]] = relationship(back_populates="organization")

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="departments")
    targets: Mapped[List["Target"]] = relationship(back_populates="department")

class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(50))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="targets")
    department: Mapped["Department"] = relationship(back_populates="targets")
