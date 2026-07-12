from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Course, CourseOffering, Enrollment


class OfferingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _active_count_sq(self):
        return (
            select(
                Enrollment.offering_id.label("oid"),
                func.count().label("active"),
            )
            .where(Enrollment.status == "REGISTERED")
            .group_by(Enrollment.offering_id)
            .subquery()
        )

    async def list(
        self,
        *,
        term_id: int | None,
        course_id: int | None,
        search: str | None,
        open_only: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[CourseOffering], int]:
        sub = self._active_count_sq()
        active = func.coalesce(sub.c.active, 0)
        stmt = (
            select(CourseOffering, active)
            .outerjoin(sub, sub.c.oid == CourseOffering.id)
            .options(
                selectinload(CourseOffering.course),
                selectinload(CourseOffering.term),
            )
        )
        count_stmt = select(func.count()).select_from(CourseOffering)

        conds = []
        if term_id is not None:
            conds.append(CourseOffering.term_id == term_id)
        if course_id is not None:
            conds.append(CourseOffering.course_id == course_id)
        if open_only:
            conds.append(CourseOffering.status == "OPEN")
        for c in conds:
            stmt = stmt.where(c)
            count_stmt = count_stmt.where(c)

        if search:
            like = f"%{search}%"
            search_cond = or_(Course.title.ilike(like), Course.course_code.ilike(like))
            stmt = stmt.join(Course, Course.id == CourseOffering.course_id).where(search_cond)
            count_stmt = count_stmt.join(Course, Course.id == CourseOffering.course_id).where(
                search_cond
            )

        total = (await self.db.execute(count_stmt)).scalar_one()
        rows = (
            await self.db.execute(stmt.order_by(CourseOffering.id).offset(offset).limit(limit))
        ).all()
        offerings: list[CourseOffering] = []
        for offering, active_count in rows:
            offering.available_seats = offering.capacity - int(active_count)
            offerings.append(offering)
        return offerings, total

    async def get_detail(self, offering_id: int) -> CourseOffering | None:
        sub = self._active_count_sq()
        active = func.coalesce(sub.c.active, 0)
        row = (
            await self.db.execute(
                select(CourseOffering, active)
                .outerjoin(sub, sub.c.oid == CourseOffering.id)
                .options(
                    selectinload(CourseOffering.course),
                    selectinload(CourseOffering.term),
                )
                .where(CourseOffering.id == offering_id)
            )
        ).first()
        if row is None:
            return None
        offering, active_count = row
        offering.available_seats = offering.capacity - int(active_count)
        return offering

    async def get_for_update(self, offering_id: int) -> CourseOffering | None:
        """Fetch the offering row with a FOR UPDATE lock (Postgres). This
        serializes concurrent registrations for the same offering so the
        capacity check below can't overbook. (No-op on SQLite.)"""
        return (
            await self.db.execute(
                select(CourseOffering).where(CourseOffering.id == offering_id).with_for_update()
            )
        ).scalar_one_or_none()

    async def active_count(self, offering_id: int) -> int:
        return (
            await self.db.execute(
                select(func.count())
                .select_from(Enrollment)
                .where(Enrollment.offering_id == offering_id, Enrollment.status == "REGISTERED")
            )
        ).scalar_one()

    async def active_offerings_for_student_in_term(
        self, student_id: int, term_id: int
    ) -> Sequence[CourseOffering]:
        rows = (
            (
                await self.db.execute(
                    select(CourseOffering)
                    .join(Enrollment, Enrollment.offering_id == CourseOffering.id)
                    .where(
                        Enrollment.student_id == student_id,
                        Enrollment.status == "REGISTERED",
                        CourseOffering.term_id == term_id,
                    )
                    .options(selectinload(CourseOffering.course))
                )
            )
            .scalars()
            .all()
        )
        return list(rows)
