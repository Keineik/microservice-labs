from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.offering import CourseOffering


class Course(TimestampMixin, Base):
    """Catalog entry — the abstract course, independent of any term."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(Integer)
    department: Mapped[str | None] = mapped_column(String(100), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    offerings: Mapped[list[CourseOffering]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
