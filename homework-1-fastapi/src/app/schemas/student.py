from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StudentBase(BaseModel):
    student_code: str = Field(max_length=20, examples=["SV00001"])
    full_name: str = Field(max_length=200, examples=["Nguyen Van A"])
    email: EmailStr = Field(examples=["sv00001@univ.edu"])
    major: str | None = Field(default=None, max_length=100, examples=["Computer Science"])
    enrollment_year: int | None = Field(default=None, ge=1990, le=2100, examples=[2023])


class StudentCreate(StudentBase):
    pass


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
