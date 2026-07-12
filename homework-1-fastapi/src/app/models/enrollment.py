from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, utcnow

if TYPE_CHECKING:
    from app.models.offering import CourseOffering
    from app.models.student import Student


class Enrollment(TimestampMixin, Base):
    """A student's registration in a course offering.

    status: REGISTERED (active) -> DROPPED (cancelled) | COMPLETED (past, has grade).
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        # At most one ACTIVE registration per (student, offering). Dropped/completed
        # rows are kept for history, so this must be a *partial* unique index.
        # Supported on both Postgres (real DB) and SQLite (tests).
        Index(
            "uq_active_enrollment",
            "student_id",
            "offering_id",
            unique=True,
            postgresql_where=text("status = 'REGISTERED'"),
            sqlite_where=text("status = 'REGISTERED'"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    offering_id: Mapped[int] = mapped_column(
        ForeignKey("course_offerings.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="REGISTERED")
    grade: Mapped[float | None] = mapped_column(Float, default=None)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    dropped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    student: Mapped[Student] = relationship(back_populates="enrollments")
    offering: Mapped[CourseOffering] = relationship(back_populates="enrollments")
