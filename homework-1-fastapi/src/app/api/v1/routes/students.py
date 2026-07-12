from fastapi import APIRouter, Depends, Query

from app.api.deps import Pagination, get_student_service
from app.schemas.common import Page, Problem
from app.schemas.student import StudentOut
from app.services.student import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=Page[StudentOut], summary="List students (search + paginate)")
async def list_students(
    search: str | None = Query(None, description="match on name / code / email"),
    pagination: Pagination = Depends(),
    service: StudentService = Depends(get_student_service),
) -> Page[StudentOut]:
    items, total = await service.list(
        search=search, offset=pagination.offset, limit=pagination.limit
    )
    return Page[StudentOut](
        items=[StudentOut.model_validate(s) for s in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{student_id}",
    response_model=StudentOut,
    responses={404: {"model": Problem}},
    summary="Get a student by id",
)
async def get_student(
    student_id: int, service: StudentService = Depends(get_student_service)
) -> StudentOut:
    return StudentOut.model_validate(await service.get(student_id))
