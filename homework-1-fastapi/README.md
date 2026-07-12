# Enrollment API — FastAPI + Postgres (UDPT2026 Homework 1)

A student **course-enrollment** REST API. The domain (Student ↔ Enrollment ↔ Course)
deliberately matches the Spring Boot lab (`lab-1-springboot`), so the same model
carries over when that lab splits it into separate microservices.

## Domain / ERD

```
┌───────────┐        ┌───────────────┐        ┌──────────┐
│  students │ 1    * │  enrollments  │ *    1 │ courses  │
│───────────│────────│───────────────│────────│──────────│
│ id (PK)   │        │ id (PK)       │        │ id (PK)  │
│ student_  │        │ student_id FK │        │ course_  │
│  code (U) │        │ course_id  FK │        │  code (U)│
│ full_name │        │ semester      │        │ title    │
│ email (U) │        │ status        │        │ credits  │
│ major     │        │ grade         │        │ capacity │
│ ...       │        │ (uniq: s+c+sem)        │ ...      │
└───────────┘        └───────────────┘        └──────────┘
```
`idempotency_keys` is a 4th table backing safe POST retries.

## Architecture (layered)

```
routes (api/v1)  →  services  →  repositories  →  db (SQLAlchemy async)
     │                 │              │
   schemas (Pydantic contract) crosses all layers
```
Dependencies flow one direction only. Wiring is done with FastAPI's
`Depends` (see `app/api/deps.py`).

## Run it (Docker Compose)

Prereqs: a running Docker engine (Colima is fine) + `docker compose`.

```bash
make up      # build + start api and postgres; migrations run automatically
make seed    # populate 150 students / 100 courses / ~400 enrollments
```

- Swagger UI: http://localhost:8000/docs
- ReDoc:      http://localhost:8000/redoc
- OpenAPI:    http://localhost:8000/openapi.json
- Health:     http://localhost:8000/health

```bash
make logs    # tail api logs
make psql    # psql shell into postgres
make down    # stop (keep data)     |   make clean = stop + drop volume
```

## Load testing (assignment BT1)

```bash
make load    # starts Locust; open http://localhost:8089
```
Point it at the `api` host (preset), set users/spawn-rate, run, and read the
stats table for your report. Headless example is in `load/locustfile.py`.

## Endpoints (all under `/api/v1`)

| Method | Path | Description | Codes |
|---|---|---|---|
| GET  | `/students` | list + `?search=&page=&size=` | 200 |
| GET  | `/students/{id}` | get one | 200, 404 |
| POST | `/students` | create | 201, 409, 422 |
| GET  | `/courses` | list + search | 200 |
| GET  | `/courses/{id}` | get one | 200, 404 |
| POST | `/courses` | create | 201, 409, 422 |
| POST | `/enrollments` | enroll (accepts `Idempotency-Key`) | 201, 404, 409 |
| GET  | `/enrollments/{id}` | enrollment + student + course | 200, 404 |
| GET  | `/students/{id}/enrollments` | a student's enrollments | 200, 404 |

## How each requirement is met

- **Contract** — Pydantic schemas in `app/schemas/` → auto OpenAPI/Swagger.
- **DI** — `app/api/deps.py`; comparison write-up in [`docs/di_vs_no_di.md`](docs/di_vs_no_di.md).
- **REST Level 2** — correct verbs + status codes (201/204-style, 404, 409, 422).
- **RFC 7807** — `app/core/problems.py` renders every error as `application/problem+json`.
- **Idempotency** — `Idempotency-Key` header on `POST /enrollments` (`app/services/enrollment.py`).
- **API versioning** — path-based: everything under `/api/v1` (`app/api/v1/`).
- **Seed data** — `scripts/seed_data.py` (Faker, 100+ rows/table, idempotent).
- **Migrations** — Alembic (`migrations/`), applied on container start.

## Local dev (without Docker) — needs `uv` + Python 3.12

```bash
make install   # uv sync --extra dev
make test      # pytest on in-memory SQLite (no Postgres needed)
make lint      # ruff + mypy
make dev       # uvicorn --reload (expects a reachable Postgres; see .env.example)
```

Config is environment-driven (`APP_*`); copy `.env.example` → `.env` for local runs.
