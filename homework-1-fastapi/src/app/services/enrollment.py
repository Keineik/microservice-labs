from datetime import UTC, datetime, time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.problems import ConflictError, NotFoundError
from app.models import CourseOffering, Enrollment, Term
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.idempotency import IdempotencyRepository
from app.repositories.offering import OfferingRepository
from app.repositories.student import StudentRepository
from app.schemas.enrollment import EnrollmentCreate


def _as_aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _overlaps(a_start: time, a_end: time, b_start: time, b_end: time) -> bool:
    return a_start < b_end and b_start < a_end


class EnrollmentService:
    """Owns the registration transaction. Depends on several repositories +
    the session (to control commit/rollback and lock rows)."""

    def __init__(
        self,
        db: AsyncSession,
        repo: EnrollmentRepository,
        students: StudentRepository,
        offerings: OfferingRepository,
        idempotency: IdempotencyRepository,
    ) -> None:
        self.db = db
        self.repo = repo
        self.students = students
        self.offerings = offerings
        self.idempotency = idempotency

    async def get_detail(self, enrollment_id: int) -> Enrollment:
        enrollment = await self.repo.get_detail(enrollment_id)
        if enrollment is None:
            raise NotFoundError(f"Enrollment {enrollment_id} does not exist")
        return enrollment

    async def list_for_student(
        self, student_id: int, *, status: str | None = None, term_id: int | None = None
    ) -> list[Enrollment]:
        if await self.students.get(student_id) is None:
            raise NotFoundError(f"Student {student_id} does not exist")
        return await self.repo.list_for_student(student_id, status=status, term_id=term_id)

    def _registration_open(self, term: Term) -> bool:
        now = datetime.now(UTC)
        return _as_aware(term.registration_starts_at) <= now <= _as_aware(term.registration_ends_at)

    async def register(
        self, data: EnrollmentCreate, *, idempotency_key: str | None, path: str
    ) -> Enrollment:
        # Idempotency: a retry with the same key returns the original enrollment.
        if idempotency_key:
            existing = await self.idempotency.get(idempotency_key)
            if existing and existing.resource_id:
                prior = await self.repo.get(existing.resource_id)
                if prior:
                    return prior

        # Lock the student row first, then the offering row (always in this
        # order, so concurrent registrations can't deadlock). Locking the student
        # serializes that student's own registrations, making the duplicate- and
        # schedule-clash checks race-free; locking the offering prevents
        # overbooking across students.
        if await self.students.get_for_update(data.student_id) is None:
            raise NotFoundError(f"Student {data.student_id} does not exist")

        offering = await self.offerings.get_for_update(data.offering_id)
        if offering is None:
            raise NotFoundError(f"Offering {data.offering_id} does not exist")
        if offering.status != "OPEN":
            raise ConflictError(f"Offering {offering.id} is not open (status {offering.status})")

        term = await self.db.get(Term, offering.term_id)
        if term is None or not self._registration_open(term):
            raise ConflictError(
                f"Registration is closed for term {term.code if term else offering.term_id}"
            )

        if await self.repo.get_active(data.student_id, offering.id):
            raise ConflictError("Student is already registered for this offering")

        if await self.offerings.active_count(offering.id) >= offering.capacity:
            raise ConflictError(f"Offering {offering.id} is full (capacity {offering.capacity})")

        # Weekly schedule clash with the student's other registrations this term.
        for other in await self.offerings.active_offerings_for_student_in_term(
            data.student_id, offering.term_id
        ):
            if other.day_of_week == offering.day_of_week and _overlaps(
                offering.start_time, offering.end_time, other.start_time, other.end_time
            ):
                raise ConflictError(
                    f"Time clash with {other.course.course_code} on {other.day_of_week}"
                )

        enrollment = Enrollment(
            student_id=data.student_id, offering_id=offering.id, status="REGISTERED"
        )
        try:
            await self.repo.add(enrollment)
            if idempotency_key:
                await self.idempotency.add(
                    key=idempotency_key,
                    method="POST",
                    path=path,
                    status_code=201,
                    resource_id=enrollment.id,
                )
            await self.db.commit()
        except IntegrityError:
            # Backstop for anything that slipped past the checks above under
            # concurrency: a duplicate active enrollment (partial unique index)
            # or a racing request with the same idempotency key. Turn it into a
            # clean replay or 409 instead of a 500.
            await self.db.rollback()
            if idempotency_key:
                prior_key = await self.idempotency.get(idempotency_key)
                if prior_key and prior_key.resource_id:
                    prior = await self.repo.get(prior_key.resource_id)
                    if prior:
                        return prior
            raise ConflictError("Student is already registered for this offering") from None
        await self.db.refresh(enrollment)
        return enrollment

    async def cancel(self, enrollment_id: int) -> None:
        enrollment = await self.repo.get(enrollment_id)
        if enrollment is None or enrollment.status != "REGISTERED":
            raise NotFoundError(f"Active enrollment {enrollment_id} does not exist")
        offering = await self.db.get(CourseOffering, enrollment.offering_id)
        term = await self.db.get(Term, offering.term_id) if offering else None
        if offering is None or term is None:
            # FK integrity guarantees both exist; this narrows types for mypy.
            raise NotFoundError(f"Active enrollment {enrollment_id} does not exist")
        if not self._registration_open(term):
            raise ConflictError(
                f"Registration for term {term.code} is closed; cannot drop this enrollment"
            )
        enrollment.status = "DROPPED"
        enrollment.dropped_at = datetime.now(UTC)
        await self.db.commit()
