from fastapi import APIRouter, Depends, Header, Query, Request, status

from app.api.deps import get_enrollment_service
from app.schemas.common import Problem
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentOut,
    EnrollmentStatus,
    EnrollmentWithOffering,
    ScheduleItem,
)
from app.services.enrollment import EnrollmentService

router = APIRouter(tags=["enrollments"])


@router.post(
    "/enrollments",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": Problem}, 409: {"model": Problem}},
    summary="Register a student in an offering (supports Idempotency-Key header)",
)
async def register(
    payload: EnrollmentCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    service: EnrollmentService = Depends(get_enrollment_service),
) -> EnrollmentOut:
    enrollment = await service.register(
        payload, idempotency_key=idempotency_key, path=request.url.path
    )
    return EnrollmentOut.model_validate(enrollment)


@router.get(
    "/enrollments/{enrollment_id}",
    response_model=EnrollmentWithOffering,
    responses={404: {"model": Problem}},
    summary="Get an enrollment with its offering (course + term + schedule)",
)
async def get_enrollment(
    enrollment_id: int, service: EnrollmentService = Depends(get_enrollment_service)
) -> EnrollmentWithOffering:
    return EnrollmentWithOffering.model_validate(await service.get_detail(enrollment_id))


@router.delete(
    "/enrollments/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": Problem}, 409: {"model": Problem}},
    summary="Cancel (drop) a registration — allowed while the term's registration is open",
)
async def cancel_enrollment(
    enrollment_id: int, service: EnrollmentService = Depends(get_enrollment_service)
) -> None:
    await service.cancel(enrollment_id)


@router.get(
    "/students/{student_id}/enrollments",
    response_model=list[EnrollmentWithOffering],
    responses={404: {"model": Problem}},
    summary="A student's enrollments — transcript (COMPLETED + grade) and current (REGISTERED)",
)
async def list_student_enrollments(
    student_id: int,
    status_filter: EnrollmentStatus | None = Query(
        None, alias="status", description="filter by enrollment status"
    ),
    term_id: int | None = Query(None, description="filter to one term"),
    service: EnrollmentService = Depends(get_enrollment_service),
) -> list[EnrollmentWithOffering]:
    enrollments = await service.list_for_student(
        student_id,
        status=status_filter.value if status_filter else None,
        term_id=term_id,
    )
    return [EnrollmentWithOffering.model_validate(e) for e in enrollments]


@router.get(
    "/students/{student_id}/schedule",
    response_model=list[ScheduleItem],
    responses={404: {"model": Problem}},
    summary="A student's weekly schedule (registered offerings) for a term",
)
async def student_schedule(
    student_id: int,
    term_id: int = Query(..., description="term to build the schedule for"),
    service: EnrollmentService = Depends(get_enrollment_service),
) -> list[ScheduleItem]:
    enrollments = await service.list_for_student(student_id, status="REGISTERED", term_id=term_id)
    return [
        ScheduleItem(
            enrollment_id=e.id,
            course_code=e.offering.course.course_code,
            course_title=e.offering.course.title,
            section_no=e.offering.section_no,
            instructor=e.offering.instructor,
            day_of_week=e.offering.day_of_week,
            start_time=e.offering.start_time,
            end_time=e.offering.end_time,
            room=e.offering.room,
        )
        for e in enrollments
    ]
