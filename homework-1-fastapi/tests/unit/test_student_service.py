"""Unit tests for StudentService with fake collaborators — no DB, no HTTP.

Possible only because the service receives its dependencies (DI); we hand it
fakes instead of a real repository/session.
"""

import pytest

from app.core.problems import ConflictError, NotFoundError
from app.schemas.student import StudentCreate
from app.services.student import StudentService


class FakeStudentRepo:
    def __init__(self, by_code=None, by_email=None) -> None:
        self._by_code = by_code
        self._by_email = by_email
        self.added: list = []

    async def get(self, student_id):
        return None

    async def get_by_code(self, code):
        return self._by_code

    async def get_by_email(self, email):
        return self._by_email

    async def add(self, student):
        student.id = 1
        self.added.append(student)
        return student


class FakeSession:
    async def commit(self):  # noqa: D401 - test double
        pass

    async def refresh(self, obj):
        pass


async def test_create_rejects_duplicate_code():
    service = StudentService(FakeSession(), FakeStudentRepo(by_code=object()))
    with pytest.raises(ConflictError):
        await service.create(
            StudentCreate(student_code="SV1", full_name="A", email="a@univ.edu")
        )


async def test_create_rejects_duplicate_email():
    service = StudentService(FakeSession(), FakeStudentRepo(by_email=object()))
    with pytest.raises(ConflictError):
        await service.create(
            StudentCreate(student_code="SV1", full_name="A", email="a@univ.edu")
        )


async def test_get_missing_raises_not_found():
    service = StudentService(FakeSession(), FakeStudentRepo())
    with pytest.raises(NotFoundError):
        await service.get(999)


async def test_create_succeeds_and_persists():
    repo = FakeStudentRepo()
    service = StudentService(FakeSession(), repo)
    student = await service.create(
        StudentCreate(student_code="SV1", full_name="A", email="a@univ.edu")
    )
    assert student.id == 1
    assert len(repo.added) == 1
