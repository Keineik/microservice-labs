from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Enrollment


class EnrollmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, enrollment_id: int) -> Enrollment | None:
        return await self.db.get(Enrollment, enrollment_id)

    async def get_detail(self, enrollment_id: int) -> Enrollment | None:
        res = await self.db.execute(
            select(Enrollment)
            .options(selectinload(Enrollment.student), selectinload(Enrollment.course))
            .where(Enrollment.id == enrollment_id)
        )
        return res.scalar_one_or_none()

    async def get_unique(
        self, student_id: int, course_id: int, semester: str
    ) -> Enrollment | None:
        res = await self.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id,
                Enrollment.semester == semester,
            )
        )
        return res.scalar_one_or_none()

    async def list_for_student(self, student_id: int) -> list[Enrollment]:
        res = await self.db.execute(
            select(Enrollment)
            .options(selectinload(Enrollment.course))
            .where(Enrollment.student_id == student_id)
            .order_by(Enrollment.id)
        )
        return list(res.scalars().all())

    async def add(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment
