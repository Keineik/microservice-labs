from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course


class CourseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, course_id: int) -> Course | None:
        return await self.db.get(Course, course_id)

    async def list(
        self, *, search: str | None, offset: int, limit: int
    ) -> tuple[list[Course], int]:
        stmt = select(Course)
        count_stmt = select(func.count()).select_from(Course)
        if search:
            like = f"%{search}%"
            cond = or_(Course.title.ilike(like), Course.course_code.ilike(like))
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)
        total = (await self.db.execute(count_stmt)).scalar_one()
        rows = (
            (await self.db.execute(stmt.order_by(Course.course_code).offset(offset).limit(limit)))
            .scalars()
            .all()
        )
        return list(rows), total
