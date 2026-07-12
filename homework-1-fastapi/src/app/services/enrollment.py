from sqlalchemy.ext.asyncio import AsyncSession

from app.core.problems import ConflictError, NotFoundError
from app.models import Enrollment
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.idempotency import IdempotencyRepository
from app.repositories.student import StudentRepository
from app.schemas.enrollment import EnrollmentCreate


class EnrollmentService:
    """Depends on four repositories + the session — a clear example of DI
    composing collaborators. Mirrors the Spring Boot Enrollment service that
    calls Student + Course services."""

    def __init__(
        self,
        db: AsyncSession,
        repo: EnrollmentRepository,
        students: StudentRepository,
        courses: CourseRepository,
        idempotency: IdempotencyRepository,
    ) -> None:
        self.db = db
        self.repo = repo
        self.students = students
        self.courses = courses
        self.idempotency = idempotency

    async def get_detail(self, enrollment_id: int) -> Enrollment:
        enrollment = await self.repo.get_detail(enrollment_id)
        if enrollment is None:
            raise NotFoundError(f"Enrollment {enrollment_id} does not exist")
        return enrollment

    async def list_for_student(self, student_id: int) -> list[Enrollment]:
        if await self.students.get(student_id) is None:
            raise NotFoundError(f"Student {student_id} does not exist")
        return await self.repo.list_for_student(student_id)

    async def create(
        self, data: EnrollmentCreate, *, idempotency_key: str | None, path: str
    ) -> Enrollment:
        # Idempotency: a retry with the same key returns the original resource.
        if idempotency_key:
            existing = await self.idempotency.get(idempotency_key)
            if existing and existing.resource_id:
                enrollment = await self.repo.get(existing.resource_id)
                if enrollment:
                    return enrollment

        # Cross-entity validation (404 if a referenced entity is missing).
        if await self.students.get(data.student_id) is None:
            raise NotFoundError(f"Student {data.student_id} does not exist")
        if await self.courses.get(data.course_id) is None:
            raise NotFoundError(f"Course {data.course_id} does not exist")

        # Business rule: no duplicate enrollment for the same semester.
        if await self.repo.get_unique(data.student_id, data.course_id, data.semester):
            raise ConflictError(
                "Student is already enrolled in this course for the given semester"
            )

        enrollment = Enrollment(**data.model_dump())
        await self.repo.add(enrollment)
        if idempotency_key:
            await self.idempotency.add(
                key=idempotency_key,
                method="POST",
                path=path,
                status_code=201,
                resource_id=enrollment.id,
            )
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment
