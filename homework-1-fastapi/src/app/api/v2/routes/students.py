from fastapi import APIRouter, Depends, Query

from app.api.deps import Pagination, get_student_service
from app.models import Student
from app.schemas.common import Page, Problem
from app.schemas.student import StudentOutV2
from app.services.student import StudentService

# Same service/repository layer as v1 — only the *representation* differs.
# Versioning is a presentation concern; business logic is reused, not forked.
router = APIRouter(prefix="/students", tags=["students (v2)"])


def _to_v2(student: Student) -> StudentOutV2:
    return StudentOutV2(
        id=student.id,
        code=student.student_code,
        name=student.full_name,
        email=student.email,
        major=student.major,
        enrollment_year=student.enrollment_year,
    )


@router.get(
    "",
    response_model=Page[StudentOutV2],
    summary="List students (v2 contract: code/name, no timestamps)",
)
async def list_students(
    search: str | None = Query(None, description="match on name / code / email"),
    pagination: Pagination = Depends(),
    service: StudentService = Depends(get_student_service),
) -> Page[StudentOutV2]:
    items, total = await service.list(
        search=search, offset=pagination.offset, limit=pagination.limit
    )
    return Page[StudentOutV2](
        items=[_to_v2(s) for s in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{student_id}",
    response_model=StudentOutV2,
    responses={404: {"model": Problem}},
    summary="Get a student by id (v2 contract)",
)
async def get_student(
    student_id: int, service: StudentService = Depends(get_student_service)
) -> StudentOutV2:
    return _to_v2(await service.get(student_id))
