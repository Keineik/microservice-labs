"""Dependency-injection providers.

Each is a small per-request factory. They all depend (transitively) on
``get_db``, and FastAPI caches a dependency's result within a request, so every
repository/service in one request shares the same session — letting a service
commit a single transaction.
"""

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.idempotency import IdempotencyRepository
from app.repositories.offering import OfferingRepository
from app.repositories.student import StudentRepository
from app.repositories.term import TermRepository
from app.services.course import CourseService
from app.services.enrollment import EnrollmentService
from app.services.offering import OfferingService
from app.services.student import StudentService
from app.services.term import TermService


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


def get_term_repo(db: AsyncSession = Depends(get_db)) -> TermRepository:
    return TermRepository(db)


def get_offering_repo(db: AsyncSession = Depends(get_db)) -> OfferingRepository:
    return OfferingRepository(db)


def get_enrollment_repo(db: AsyncSession = Depends(get_db)) -> EnrollmentRepository:
    return EnrollmentRepository(db)


def get_idempotency_repo(db: AsyncSession = Depends(get_db)) -> IdempotencyRepository:
    return IdempotencyRepository(db)


# --- services -------------------------------------------------------------
def get_student_service(repo: StudentRepository = Depends(get_student_repo)) -> StudentService:
    return StudentService(repo)


def get_course_service(repo: CourseRepository = Depends(get_course_repo)) -> CourseService:
    return CourseService(repo)


def get_term_service(repo: TermRepository = Depends(get_term_repo)) -> TermService:
    return TermService(repo)


def get_offering_service(repo: OfferingRepository = Depends(get_offering_repo)) -> OfferingService:
    return OfferingService(repo)


def get_enrollment_service(
    db: AsyncSession = Depends(get_db),
    repo: EnrollmentRepository = Depends(get_enrollment_repo),
    students: StudentRepository = Depends(get_student_repo),
    offerings: OfferingRepository = Depends(get_offering_repo),
    idempotency: IdempotencyRepository = Depends(get_idempotency_repo),
) -> EnrollmentService:
    return EnrollmentService(db, repo, students, offerings, idempotency)
