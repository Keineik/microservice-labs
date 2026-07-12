from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import CourseOffering, Enrollment


class EnrollmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _with_offering(self):
        return (
            selectinload(Enrollment.offering).selectinload(CourseOffering.course),
            selectinload(Enrollment.offering).selectinload(CourseOffering.term),
        )

    async def get(self, enrollment_id: int) -> Enrollment | None:
        return await self.db.get(Enrollment, enrollment_id)

    async def get_detail(self, enrollment_id: int) -> Enrollment | None:
        return (
            await self.db.execute(
                select(Enrollment)
                .options(*self._with_offering())
                .where(Enrollment.id == enrollment_id)
            )
        ).scalar_one_or_none()

    async def get_active(self, student_id: int, offering_id: int) -> Enrollment | None:
        return (
            await self.db.execute(
                select(Enrollment).where(
                    Enrollment.student_id == student_id,
                    Enrollment.offering_id == offering_id,
                    Enrollment.status == "REGISTERED",
                )
            )
        ).scalar_one_or_none()

    async def list_for_student(
        self, student_id: int, *, status: str | None = None, term_id: int | None = None
    ) -> list[Enrollment]:
        stmt = (
            select(Enrollment)
            .options(*self._with_offering())
            .where(Enrollment.student_id == student_id)
        )
        if status is not None:
            stmt = stmt.where(Enrollment.status == status)
        if term_id is not None:
            stmt = stmt.where(Enrollment.offering.has(CourseOffering.term_id == term_id))
        stmt = stmt.order_by(Enrollment.id)
        return list((await self.db.execute(stmt)).scalars().all())

    async def add(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
