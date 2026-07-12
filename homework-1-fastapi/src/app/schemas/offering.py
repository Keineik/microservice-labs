from datetime import time
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, computed_field

from app.schemas.course import CourseSummary
from app.schemas.term import TermOut


class OfferingStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class DayOfWeek(StrEnum):
    MON = "MON"
    TUE = "TUE"
    WED = "WED"
    THU = "THU"
    FRI = "FRI"
    SAT = "SAT"
    SUN = "SUN"


class OfferingSummary(BaseModel):
    """Offering view without seat counts — for embedding in enrollments."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    section_no: str
    instructor: str | None
    status: OfferingStatus
    day_of_week: DayOfWeek
    start_time: time
    end_time: time
    room: str | None
    course: CourseSummary
    term: TermOut


class OfferingOut(OfferingSummary):
    """Full offering view for the browse/registration endpoints."""

    capacity: int
    available_seats: int

    @computed_field  # type: ignore[prop-decorator]
    @property
    def can_register(self) -> bool:
        return (
            self.status == OfferingStatus.OPEN
            and self.term.is_registration_open
            and self.available_seats > 0
        )
