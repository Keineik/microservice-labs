"""SYNC contender: Flask (WSGI) + sync SQLAlchemy + psycopg2.

Each worker blocks for the whole DB round-trip. Serve with gunicorn sync
workers (the Flask dev server is single-threaded and not representative):

    uv run --extra bench gunicorn --pythonpath benchmark -w 1 -b 0.0.0.0:9002 bench_sync:app

(or `make bench-sync`, `WEB_CONCURRENCY=N make bench-sync`). Reads the DB
seeded by the main app; run `make up && make seed` first.

Same statements, same serialization, same pool size as bench_async -> the only
difference is that this stack blocks a worker on each I/O wait.
"""

import bench_common as bc
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(bc.SYNC_URL, pool_size=bc.POOL_SIZE, max_overflow=0)
Session = sessionmaker(engine, expire_on_commit=False)

app = Flask(__name__)


def _fetch(stmt) -> list[dict]:
    with Session() as s:
        return bc.rows_to_dicts(s.execute(stmt).mappings().all())


@app.get("/offerings")
def offerings():
    stmt = bc.offerings_list_stmt(
        term_id=request.args.get("term_id", type=int),
        search=request.args.get("search", type=str),
        open_only=request.args.get("open_only", default="false").lower() == "true",
        limit=request.args.get("size", default=20, type=int),
        offset=(request.args.get("page", default=1, type=int) - 1)
        * request.args.get("size", default=20, type=int),
    )
    return jsonify(bc.with_available_seats(_fetch(stmt)))


@app.get("/offerings/<int:offering_id>")
def offering_detail(offering_id: int):
    rows = bc.with_available_seats(_fetch(bc.offering_detail_stmt(offering_id)))
    return (jsonify(rows[0]), 200) if rows else (jsonify({}), 404)


@app.get("/students/<int:student_id>/enrollments")
def enrollments(student_id: int):
    return jsonify(_fetch(bc.student_enrollments_stmt(student_id)))


@app.get("/courses")
def courses():
    size = request.args.get("size", default=20, type=int)
    page = request.args.get("page", default=1, type=int)
    return jsonify(_fetch(bc.courses_list_stmt(limit=size, offset=(page - 1) * size)))


@app.get("/io")
def io():
    seconds = request.args.get("seconds", default=bc.IO_DEFAULT_SECONDS, type=float)
    with Session() as s:
        s.execute(bc.io_sleep_stmt(seconds))
    return jsonify({"slept": seconds})
