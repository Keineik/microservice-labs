"""Unit tests with fakes — no DB, no HTTP. Possible because services receive
their dependencies via DI, so we can hand them test doubles."""

from datetime import time

import pytest

from app.core.problems import NotFoundError
from app.schemas.enrollment import EnrollmentCreate
from app.services.enrollment import EnrollmentService, _overlaps
from app.services.student import StudentService


class _FakeStudentRepo:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    async def get(self, student_id):
        return object() if self._exists else None

    async def get_for_update(self, student_id):
        return object() if self._exists else None


def test_overlaps_detects_time_clash():
    assert _overlaps(time(9, 0), time(10, 30), time(9, 30), time(11, 0)) is True
    assert _overlaps(time(9, 0), time(10, 0), time(10, 0), time(11, 0)) is False  # back-to-back
    assert _overlaps(time(9, 0), time(10, 0), time(13, 0), time(14, 0)) is False


async def test_student_service_get_missing_raises_not_found():
    service = StudentService(_FakeStudentRepo(exists=False))
    with pytest.raises(NotFoundError):
        await service.get(999)


async def test_register_unknown_student_raises_not_found():
    # With no idempotency key, register checks the student first and bails out
    # before touching the offering/session — so None deps are never used.
    service = EnrollmentService(
        db=None,
        repo=None,
        students=_FakeStudentRepo(exists=False),
        offerings=None,
        idempotency=None,
    )
    with pytest.raises(NotFoundError):
        await service.register(
            EnrollmentCreate(student_id=1, offering_id=1), idempotency_key=None, path="/x"
        )
