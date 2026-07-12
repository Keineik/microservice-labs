"""Dependency-injection providers.

Each provider is a small factory FastAPI resolves per request. Because they all
depend (directly or transitively) on ``get_db``, and FastAPI caches a dependency
result within a request, every repository/service in one request shares the same
session — so ``service.create()`` can commit a single transaction.
"""

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.idempotency import IdempotencyRepository
from app.repositories.student import StudentRepository
from app.services.course import CourseService
from app.services.enrollment import EnrollmentService
from app.services.student import StudentService


class Pagination:
    """Reusable pagination query params: ``?page=1&size=20``."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-based page number"),
        size: int = Query(20, ge=1, le=100, description="page size (max 100)"),
    ) -> None:
        self.page = page
        self.size = size
        self.offset = (page - 1) * size
        self.limit = size


# --- repositories ---------------------------------------------------------
def get_student_repo(db: AsyncSession = Depends(get_db)) -> StudentRepository:
    return StudentRepository(db)


def get_course_repo(db: AsyncSession = Depends(get_db)) -> CourseRepository:
    return CourseRepository(db)


def get_enrollment_repo(db: AsyncSession = Depends(get_db)) -> EnrollmentRepository:
    return EnrollmentRepository(db)


def get_idempotency_repo(db: AsyncSession = Depends(get_db)) -> IdempotencyRepository:
    return IdempotencyRepository(db)


# --- services -------------------------------------------------------------
def get_student_service(
    db: AsyncSession = Depends(get_db),
    repo: StudentRepository = Depends(get_student_repo),
) -> StudentService:
    return StudentService(db, repo)


def get_course_service(
    db: AsyncSession = Depends(get_db),
    repo: CourseRepository = Depends(get_course_repo),
) -> CourseService:
    return CourseService(db, repo)


def get_enrollment_service(
    db: AsyncSession = Depends(get_db),
    repo: EnrollmentRepository = Depends(get_enrollment_repo),
    students: StudentRepository = Depends(get_student_repo),
    courses: CourseRepository = Depends(get_course_repo),
    idempotency: IdempotencyRepository = Depends(get_idempotency_repo),
) -> EnrollmentService:
    return EnrollmentService(db, repo, students, courses, idempotency)
