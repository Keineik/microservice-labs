from fastapi import APIRouter, Depends, Query

from app.api.deps import Pagination, get_course_service
from app.schemas.common import Page, Problem
from app.schemas.course import CourseOut
from app.services.course import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=Page[CourseOut], summary="List catalog courses (search + paginate)")
async def list_courses(
    search: str | None = Query(None, description="match on title / code"),
    pagination: Pagination = Depends(),
    service: CourseService = Depends(get_course_service),
) -> Page[CourseOut]:
    items, total = await service.list(
        search=search, offset=pagination.offset, limit=pagination.limit
    )
    return Page[CourseOut](
        items=[CourseOut.model_validate(c) for c in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{course_id}",
    response_model=CourseOut,
    responses={404: {"model": Problem}},
    summary="Get a catalog course by id",
)
async def get_course(
    course_id: int, service: CourseService = Depends(get_course_service)
) -> CourseOut:
    return CourseOut.model_validate(await service.get(course_id))
