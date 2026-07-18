"""Shared query + serialization code for the sync/async benchmark apps.

Both `bench_async.py` (FastAPI + asyncpg) and `bench_sync.py` (Flask + psycopg2)
import this module and run the SAME SQLAlchemy statements and the SAME
serialization, so the only variable under test is the concurrency model
(async event loop vs sync worker blocking on I/O).

The statements select explicit columns (no ORM lazy-loading / relationship
loaders) so behaviour is identical and deterministic across the sync and async
drivers. Models are reused from the main app (`app.models`), so the schema is
exactly the one the API and seed script created.
"""

from __future__ import annotations

import datetime as dt
import os
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select, text
from sqlalchemy.sql import Select

from app.models import Course, CourseOffering, Enrollment

# --- Config (one source of truth, shared by both apps) --------------------
# Same database, same pool size -> a different pool would silently change DB
# concurrency and invalidate the comparison.
_BASE_DSN = os.getenv("BENCH_DSN", "app:app@localhost:5432/enrollment")
ASYNC_URL = f"postgresql+asyncpg://{_BASE_DSN}"
SYNC_URL = f"postgresql+psycopg2://{_BASE_DSN}"
# Pool set high so it is NOT the bottleneck — the ceiling should come from the
# concurrency model + CPU, not an artificially small pool. Note each worker
# process has its own pool, so total DB connections = workers x POOL_SIZE
# (Postgres max_connections is raised to match in docker-compose).
POOL_SIZE = int(os.getenv("BENCH_POOL_SIZE", "100"))
# Default DB sleep for the /io scenario, in seconds (0.1 = 100 ms). Override
# per request with ?seconds=, or globally with BENCH_IO_SECONDS.
IO_DEFAULT_SECONDS = float(os.getenv("BENCH_IO_SECONDS", "0.1"))


# --- Serialization (identical payloads on both sides) ---------------------
def _jsonable(value: Any) -> Any:
    if isinstance(value, dt.datetime | dt.date | dt.time):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def rows_to_dicts(rows: Any) -> list[dict[str, Any]]:
    """Turn SQLAlchemy Row objects (via .mappings()) into plain JSON-safe dicts."""
    return [{k: _jsonable(v) for k, v in row.items()} for row in rows]


# --- Statements -----------------------------------------------------------
def _active_count_subq():
    # Correlated scalar subquery: number of active (REGISTERED) enrollments for
    # each offering. Used to derive available_seats, like the real API.
    return (
        select(func.count())
        .select_from(Enrollment)
        .where(
            Enrollment.offering_id == CourseOffering.id,
            Enrollment.status == "REGISTERED",
        )
        .correlate(CourseOffering)
        .scalar_subquery()
    )


def offerings_list_stmt(
    *, term_id: int | None, search: str | None, open_only: bool, limit: int, offset: int
) -> Select:
    stmt = select(
        CourseOffering.id,
        CourseOffering.section_no,
        CourseOffering.status,
        CourseOffering.day_of_week,
        CourseOffering.start_time,
        CourseOffering.end_time,
        CourseOffering.room,
        CourseOffering.capacity,
        CourseOffering.instructor,
        Course.course_code,
        Course.title,
        Course.credits,
        _active_count_subq().label("active"),
    ).join(Course, Course.id == CourseOffering.course_id)
    if term_id is not None:
        stmt = stmt.where(CourseOffering.term_id == term_id)
    if open_only:
        stmt = stmt.where(CourseOffering.status == "OPEN")
    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Course.title.ilike(like), Course.course_code.ilike(like)))
    return stmt.order_by(CourseOffering.id).limit(limit).offset(offset)


def offering_detail_stmt(offering_id: int) -> Select:
    return (
        select(
            CourseOffering.id,
            CourseOffering.section_no,
            CourseOffering.status,
            CourseOffering.day_of_week,
            CourseOffering.start_time,
            CourseOffering.end_time,
            CourseOffering.room,
            CourseOffering.capacity,
            CourseOffering.instructor,
            Course.course_code,
            Course.title,
            Course.credits,
            _active_count_subq().label("active"),
        )
        .join(Course, Course.id == CourseOffering.course_id)
        .where(CourseOffering.id == offering_id)
    )


def student_enrollments_stmt(student_id: int) -> Select:
    return (
        select(
            Enrollment.id,
            Enrollment.status,
            Enrollment.grade,
            Course.course_code,
            Course.title,
            Course.credits,
            CourseOffering.section_no,
            CourseOffering.day_of_week,
            CourseOffering.start_time,
            CourseOffering.end_time,
            CourseOffering.room,
        )
        .join(CourseOffering, CourseOffering.id == Enrollment.offering_id)
        .join(Course, Course.id == CourseOffering.course_id)
        .where(Enrollment.student_id == student_id)
        .order_by(Enrollment.id)
    )


def courses_list_stmt(*, limit: int, offset: int) -> Select:
    return (
        select(
            Course.id,
            Course.course_code,
            Course.title,
            Course.credits,
            Course.department,
        )
        .order_by(Course.id)
        .limit(limit)
        .offset(offset)
    )


# Deliberately I/O-bound query to isolate/dramatize the sync-vs-async effect:
# pg_sleep makes each request wait on the DB, so async (one loop) overlaps many
# waits while a single sync worker serializes them.
def io_sleep_stmt(seconds: float):
    return text("SELECT pg_sleep(:s)").bindparams(s=seconds)


def with_available_seats(dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add available_seats = capacity - active to offering dicts."""
    for d in dicts:
        if "capacity" in d and "active" in d:
            d["available_seats"] = d["capacity"] - int(d.pop("active"))
    return dicts
