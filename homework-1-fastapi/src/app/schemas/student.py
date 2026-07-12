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


class StudentOutV2(BaseModel):
    """v2 representation of a student.

    A deliberately *breaking* contract change from :class:`StudentOut`, used to
    demonstrate API versioning: fields are renamed to a cleaner public contract
    (``student_code`` → ``code``, ``full_name`` → ``name``) and internal audit
    timestamps are dropped. v1 clients keep using ``/api/v1`` unchanged; new
    clients opt into this shape at ``/api/v2``. The mapping from the ORM model
    is done explicitly in the v2 route.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    email: EmailStr
    major: str | None
    enrollment_year: int | None
