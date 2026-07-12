from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.term import Term


class CourseOffering(TimestampMixin, Base):
    """A Course opened in a specific Term — the thing students register for.

    Carries the per-section capacity, meeting schedule, and status. Available
    seats = capacity - count(active REGISTERED enrollments).
    """

    __tablename__ = "course_offerings"
    __table_args__ = (
        UniqueConstraint(
            "course_id", "term_id", "section_no", name="uq_offering_course_term_section"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), index=True)
    section_no: Mapped[str] = mapped_column(String(10), default="01")
    capacity: Mapped[int] = mapped_column(Integer, default=40)
    instructor: Mapped[str | None] = mapped_column(String(200), default=None)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN / CLOSED / CANCELLED

    # Simplified single weekly meeting slot.
    day_of_week: Mapped[str] = mapped_column(String(3))  # MON..SUN
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    room: Mapped[str | None] = mapped_column(String(50), default=None)

    course: Mapped[Course] = relationship(back_populates="offerings")
    term: Mapped[Term] = relationship(back_populates="offerings")
    enrollments: Mapped[list[Enrollment]] = relationship(
        back_populates="offering", cascade="all, delete-orphan"
    )
