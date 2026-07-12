from fastapi import APIRouter, Depends, Query, status

from app.api.deps import Pagination, get_course_service
from app.schemas.common import Page, Problem
from app.schemas.course import CourseCreate, CourseOut
from app.services.course import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=Page[CourseOut], summary="List courses (search + paginate)")
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
    summary="Get a course by id",
)
async def get_course(
    course_id: int, service: CourseService = Depends(get_course_service)
) -> CourseOut:
    return CourseOut.model_validate(await service.get(course_id))


@router.post(
    "",
    response_model=CourseOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": Problem}, 422: {"model": Problem}},
    summary="Create a course",
)
async def create_course(
    payload: CourseCreate, service: CourseService = Depends(get_course_service)
) -> CourseOut:
    return CourseOut.model_validate(await service.create(payload))
