from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    course_code: str = Field(max_length=20, examples=["CS101"])
    title: str = Field(max_length=200, examples=["Introduction to Programming"])
    credits: int = Field(ge=1, le=10, examples=[3])
    department: str | None = Field(default=None, max_length=100, examples=["Computer Science"])
    capacity: int = Field(default=50, ge=1, le=1000, examples=[60])


class CourseCreate(CourseBase):
    pass


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
