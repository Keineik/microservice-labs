from app.core.problems import NotFoundError
from app.models import Student
from app.repositories.student import StudentRepository


class StudentService:
    def __init__(self, repo: StudentRepository) -> None:
        self.repo = repo

    async def get(self, student_id: int) -> Student:
        student = await self.repo.get(student_id)
        if student is None:
            raise NotFoundError(f"Student {student_id} does not exist")
        return student

    async def list(
        self, *, search: str | None, offset: int, limit: int
    ) -> tuple[list[Student], int]:
        return await self.repo.list(search=search, offset=offset, limit=limit)
