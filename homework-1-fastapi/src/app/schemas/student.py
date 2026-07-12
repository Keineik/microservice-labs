from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_code: str
    full_name: str
    email: EmailStr
    major: str | None
    enrollment_year: int | None
    created_at: datetime
    updated_at: datetime
