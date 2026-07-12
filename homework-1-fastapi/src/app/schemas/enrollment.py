from datetime import datetime, time
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.offering import OfferingSummary


class EnrollmentStatus(StrEnum):
    REGISTERED = "REGISTERED"
    DROPPED = "DROPPED"
    COMPLETED = "COMPLETED"


class EnrollmentCreate(BaseModel):
    student_id: int = Field(examples=[1])
    offering_id: int = Field(examples=[1])


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    offering_id: int
    status: EnrollmentStatus
    grade: float | None
    registered_at: datetime


class EnrollmentWithOffering(EnrollmentOut):
    """An enrollment with its offering (course + term + schedule) embedded —
    used for a student's transcript / current-registration lists."""

    offering: OfferingSummary


class ScheduleItem(BaseModel):
    """One meeting in a student's weekly schedule for a term."""

    enrollment_id: int
    course_code: str
    course_title: str
    section_no: str
    instructor: str | None
    day_of_week: str
    start_time: time
    end_time: time
    room: str | None
