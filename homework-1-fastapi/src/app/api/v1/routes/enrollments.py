from fastapi import APIRouter, Depends, Header, Request, status

from app.api.deps import get_enrollment_service
from app.schemas.common import Problem
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentDetail,
    EnrollmentOut,
    EnrollmentWithCourse,
)
from app.services.enrollment import EnrollmentService

router = APIRouter(tags=["enrollments"])


@router.post(
    "/enrollments",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": Problem}, 409: {"model": Problem}},
    summary="Enroll a student in a course (supports Idempotency-Key header)",
)
async def create_enrollment(
    payload: EnrollmentCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    service: EnrollmentService = Depends(get_enrollment_service),
) -> EnrollmentOut:
    enrollment = await service.create(
        payload, idempotency_key=idempotency_key, path=request.url.path
    )
    return EnrollmentOut.model_validate(enrollment)


@router.get(
    "/enrollments/{enrollment_id}",
    response_model=EnrollmentDetail,
    responses={404: {"model": Problem}},
    summary="Get an enrollment with student + course embedded",
)
async def get_enrollment(
    enrollment_id: int, service: EnrollmentService = Depends(get_enrollment_service)
) -> EnrollmentDetail:
    return EnrollmentDetail.model_validate(await service.get_detail(enrollment_id))


@router.get(
    "/students/{student_id}/enrollments",
    response_model=list[EnrollmentWithCourse],
    responses={404: {"model": Problem}},
    summary="List a student's enrollments (mirrors the Spring Boot Enrollment service)",
)
async def list_student_enrollments(
    student_id: int, service: EnrollmentService = Depends(get_enrollment_service)
) -> list[EnrollmentWithCourse]:
    enrollments = await service.list_for_student(student_id)
    return [EnrollmentWithCourse.model_validate(e) for e in enrollments]
