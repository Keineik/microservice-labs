from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student


class StudentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, student_id: int) -> Student | None:
        return await self.db.get(Student, student_id)

    async def get_for_update(self, student_id: int) -> Student | None:
        """Fetch the student row with a FOR UPDATE lock — serializes one
        student's concurrent registrations (no-op on SQLite)."""
        return (
            await self.db.execute(select(Student).where(Student.id == student_id).with_for_update())
        ).scalar_one_or_none()

    async def get_by_code(self, code: str) -> Student | None:
        res = await self.db.execute(select(Student).where(Student.student_code == code))
        return res.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Student | None:
        res = await self.db.execute(select(Student).where(Student.email == email))
        return res.scalar_one_or_none()

    async def list(
        self, *, search: str | None, offset: int, limit: int
    ) -> tuple[list[Student], int]:
        stmt = select(Student)
        count_stmt = select(func.count()).select_from(Student)
        if search:
            like = f"%{search}%"
            cond = or_(
                Student.full_name.ilike(like),
                Student.student_code.ilike(like),
                Student.email.ilike(like),
            )
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
        total = (await self.db.execute(count_stmt)).scalar_one()
        rows = (
            (await self.db.execute(stmt.order_by(Student.id).offset(offset).limit(limit)))
            .scalars()
            .all()
        )
        return list(rows), total

    async def add(self, student: Student) -> Student:
        self.db.add(student)
        await self.db.flush()
        await self.db.refresh(student)
        return student
