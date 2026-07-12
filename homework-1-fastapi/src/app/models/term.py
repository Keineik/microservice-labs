from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.offering import CourseOffering


class Term(TimestampMixin, Base):
    """An academic term (semester + year) with its registration window.

    Registration is open when registration_starts_at <= now <= registration_ends_at.
    """

    __tablename__ = "terms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # e.g. "2025-1"
    name: Mapped[str] = mapped_column(String(100))  # e.g. "Spring 2025"
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)
    registration_starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    offerings: Mapped[list[CourseOffering]] = relationship(
        back_populates="term", cascade="all, delete-orphan"
    )
