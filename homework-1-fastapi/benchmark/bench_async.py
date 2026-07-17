"""ASYNC contender: FastAPI (ASGI) + async SQLAlchemy + asyncpg.

One event loop overlaps many in-flight DB round-trips. Run with uvicorn:

    uv run --extra bench uvicorn bench_async:app --app-dir benchmark --port 9001

(or `make bench-async`). Reads the DB seeded by the main app; run
`make up && make seed` first.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import bench_common as bc
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(bc.ASYNC_URL, pool_size=bc.POOL_SIZE, max_overflow=0)
Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


app = FastAPI(title="bench-async (FastAPI)", lifespan=lifespan, docs_url=None, openapi_url=None)


async def _fetch(stmt) -> list[dict]:
    async with Session() as s:
        result = await s.execute(stmt)
        return bc.rows_to_dicts(result.mappings().all())


@app.get("/offerings")
async def offerings(
    term_id: int | None = None,
    search: str | None = None,
    open_only: bool = False,
    page: int = 1,
    size: int = 20,
) -> JSONResponse:
    stmt = bc.offerings_list_stmt(
        term_id=term_id,
        search=search,
        open_only=open_only,
        limit=size,
        offset=(page - 1) * size,
    )
    return JSONResponse(bc.with_available_seats(await _fetch(stmt)))


@app.get("/offerings/{offering_id}")
async def offering_detail(offering_id: int) -> JSONResponse:
    rows = bc.with_available_seats(await _fetch(bc.offering_detail_stmt(offering_id)))
    return JSONResponse(rows[0] if rows else {}, status_code=200 if rows else 404)


@app.get("/students/{student_id}/enrollments")
async def enrollments(student_id: int) -> JSONResponse:
    return JSONResponse(await _fetch(bc.student_enrollments_stmt(student_id)))


@app.get("/courses")
async def courses(page: int = 1, size: int = 20) -> JSONResponse:
    return JSONResponse(await _fetch(bc.courses_list_stmt(limit=size, offset=(page - 1) * size)))


@app.get("/io")
async def io(seconds: float = bc.IO_DEFAULT_SECONDS) -> JSONResponse:
    async with Session() as s:
        await s.execute(bc.io_sleep_stmt(seconds))
    return JSONResponse({"slept": seconds})
