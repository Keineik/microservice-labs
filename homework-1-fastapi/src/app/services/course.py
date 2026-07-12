from app.core.problems import NotFoundError
from app.models import Course
from app.repositories.course import CourseRepository


class CourseService:
    def __init__(self, repo: CourseRepository) -> None:
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
