from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseSummary(BaseModel):
    """Compact course view for embedding inside offerings/enrollments."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_code: str
    title: str
    credits: int


class CourseOut(CourseSummary):
    department: str | None = Field(default=None)
    description: str | None = Field(default=None)
    created_at: datetime
    updated_at: datetime
