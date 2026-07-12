from sqlalchemy.ext.asyncio import AsyncSession

from app.core.problems import ConflictError, NotFoundError
from app.models import Course
from app.repositories.course import CourseRepository
from app.schemas.course import CourseCreate


class CourseService:
    def __init__(self, db: AsyncSession, repo: CourseRepository) -> None:
        self.db = db
        self.repo = repo

    async def get(self, course_id: int) -> Course:
        course = await self.repo.get(course_id)
        if course is None:
            raise NotFoundError(f"Course {course_id} does not exist")
        return course

    async def list(
        self, *, search: str | None, offset: int, limit: int
    ) -> tuple[list[Course], int]:
        return await self.repo.list(search=search, offset=offset, limit=limit)

    async def create(self, data: CourseCreate) -> Course:
        if await self.repo.get_by_code(data.course_code):
            raise ConflictError(f"Course code '{data.course_code}' already exists")
        course = Course(**data.model_dump())
        await self.repo.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course
