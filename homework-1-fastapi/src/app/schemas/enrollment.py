from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.course import CourseOut
from app.schemas.student import StudentOut


class EnrollmentStatus(str, Enum):
    ENROLLED = "ENROLLED"
    DROPPED = "DROPPED"
    COMPLETED = "COMPLETED"


class EnrollmentCreate(BaseModel):
    student_id: int = Field(examples=[1])
    course_id: int = Field(examples=[1])
    semester: str = Field(max_length=20, examples=["2025-1"])


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    semester: str
    status: EnrollmentStatus
    grade: float | None
    enrolled_at: datetime


class EnrollmentWithCourse(EnrollmentOut):
    """An enrollment plus its course — used for a student's enrollment list."""

    course: CourseOut


class EnrollmentDetail(EnrollmentOut):
    """Full detail: the enrollment with both related entities embedded."""

    student: StudentOut
    course: CourseOut
