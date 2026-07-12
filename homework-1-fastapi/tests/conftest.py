from datetime import UTC, datetime, time, timedelta

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models import Base, Course, CourseOffering, Student, Term


@pytest_asyncio.fixture
async def db_engine():
    """A fresh in-memory SQLite database per test — no Postgres needed."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    """HTTP client bound to the app, with get_db overridden to the test DB.

    Overriding this one provider is the whole test setup — every layer above it
    is the real code. That is the concrete payoff of dependency injection.
    """
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as http_client:
            yield http_client
    finally:
        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample(db_engine) -> dict[str, int]:
    """Insert a small, controlled dataset directly (bypassing the read-only
    catalog API) and return the ids the tests need.

    - term:        registration OPEN now
    - closed_term: registration window in the past
    - off:         capacity 1, MON 09:00-10:30 (to test 'full')
    - off2:        capacity 10, MON 09:30-11:00 (overlaps off -> clash test)
    - off_closed:  in closed_term (to test 'registration closed')
    """
    session_maker = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    now = datetime.now(UTC)
    today = now.date()
    async with session_maker() as db:
        term = Term(
            code="T-OPEN",
            name="Open Term",
            starts_on=today,
            ends_on=today + timedelta(days=90),
            registration_starts_at=now - timedelta(days=1),
            registration_ends_at=now + timedelta(days=30),
        )
        closed_term = Term(
            code="T-CLOSED",
            name="Closed Term",
            starts_on=today - timedelta(days=120),
            ends_on=today - timedelta(days=20),
            registration_starts_at=now - timedelta(days=60),
            registration_ends_at=now - timedelta(days=30),
        )
        c1 = Course(course_code="CS101", title="Intro to CS", credits=3)
        c2 = Course(course_code="CS102", title="Data Structures", credits=3)
        s1 = Student(student_code="SV1", full_name="Alice", email="alice@univ.edu")
        s2 = Student(student_code="SV2", full_name="Bob", email="bob@univ.edu")
        db.add_all([term, closed_term, c1, c2, s1, s2])
        await db.flush()

        off = CourseOffering(
            course_id=c1.id,
            term_id=term.id,
            section_no="01",
            capacity=1,
            instructor="Dr X",
            status="OPEN",
            day_of_week="MON",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room="R1",
        )
        off2 = CourseOffering(
            course_id=c2.id,
            term_id=term.id,
            section_no="01",
            capacity=10,
            instructor="Dr Y",
            status="OPEN",
            day_of_week="MON",
            start_time=time(9, 30),
            end_time=time(11, 0),
            room="R2",
        )
        off_closed = CourseOffering(
            course_id=c1.id,
            term_id=closed_term.id,
            section_no="01",
            capacity=10,
            instructor="Dr Z",
            status="OPEN",
            day_of_week="TUE",
            start_time=time(9, 0),
            end_time=time(10, 30),
            room="R3",
        )
        db.add_all([off, off2, off_closed])
        await db.commit()

        return {
            "term": term.id,
            "closed_term": closed_term.id,
            "s1": s1.id,
            "s2": s2.id,
            "off": off.id,
            "off2": off2.id,
            "off_closed": off_closed.id,
        }
