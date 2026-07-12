from sqlalchemy.ext.asyncio import AsyncSession

from app.core.problems import ConflictError, NotFoundError
from app.models import Student
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreate


class StudentService:
    def __init__(self, db: AsyncSession, repo: StudentRepository) -> None:
        self.db = db
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

    async def create(self, data: StudentCreate) -> Student:
        if await self.repo.get_by_code(data.student_code):
            raise ConflictError(f"Student code '{data.student_code}' already exists")
        if await self.repo.get_by_email(str(data.email)):
            raise ConflictError(f"Email '{data.email}' already exists")
        student = Student(**data.model_dump())
        await self.repo.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
