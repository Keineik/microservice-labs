# Enrollment API — FastAPI + Postgres (UDPT2026 Homework, BT2 + BT3)

A simplified **student course-registration** system. Students browse the offerings
opened for a term, register (while registration is open and seats remain), view
their transcript and schedule, and cancel registrations. The domain deliberately
mirrors `lab-1-springboot` so the model carries over when that lab splits into
microservices.

> **Scope note (no auth yet):** authentication/authorization is intentionally
> out of scope for this exercise (planned for a later one). The API therefore
> takes the acting `student_id` explicitly instead of from a session/token.
> Admin operations (managing courses/terms/offerings, adding/removing students)
> are also out of scope — those are populated by the seed script. See
> [docs/design_notes.md](docs/design_notes.md).

## Domain / ERD

```
 Course ──1:*── CourseOffering ──*:1── Term
   (catalog)      (section in a term:        (semester + year +
                   capacity, schedule,         registration window)
                   instructor, status)
                        │ 1:*
                        │
                    Enrollment ──*:1── Student
             (status: REGISTERED / DROPPED / COMPLETED, grade)
```
Plus `idempotency_keys` (safe POST retries). Registration is allowed while the
**term's registration window is open**, the offering is **OPEN**, seats remain,
and there's no schedule clash.

## Run it (Docker Compose)

```bash
make up      # build + start api and postgres; migrations run on startup
make seed    # 150 students, 100 courses, 3 terms, 150 offerings, ~1.6k enrollments
```
Swagger UI → http://localhost:8000/docs · health → `/health`

```bash
make logs · make psql · make down (keep data) · make clean (drop volume) · make load
```

## API surface (all under `/api/v1`) — student-facing only

**Catalog / browse (read-only):**
| Method | Path | Notes |
|---|---|---|
| GET | `/students`, `/students/{id}` | list / detail |
| GET | `/courses`, `/courses/{id}` | catalog |
| GET | `/terms`, `/terms/{id}` | includes `is_registration_open` |
| GET | `/offerings` | filter `term_id`/`course_id`, `search`, `open_only`; returns `available_seats`, `can_register` |
| GET | `/offerings/{id}` | seats + schedule + status |

**Student activity:**
| Method | Path | Notes |
|---|---|---|
| GET | `/students/{id}/enrollments` | transcript (COMPLETED+grade) + current (REGISTERED); filter `status`/`term_id` |
| GET | `/students/{id}/schedule?term_id=` | weekly schedule for a term |
| POST | `/enrollments` | **register** (body `{student_id, offering_id}`, `Idempotency-Key` header) |
| GET | `/enrollments/{id}` | detail with offering embedded |
| DELETE | `/enrollments/{id}` | **cancel** (while registration open) → 204 |

Status codes: 201 register · 204 cancel · 404 missing · 409 (full / duplicate /
closed / schedule clash) · 422 validation. Errors are RFC 7807 `problem+json`.

## How each requirement is met

- **Contract + Swagger** — Pydantic schemas → `/docs`, `/redoc`, `/openapi.json`.
- **≥3 related tables, 100+ rows** — students/courses/offerings/enrollments (see `make seed`).
- **DI** — FastAPI `Depends` (`app/api/deps.py`) + [docs/di_vs_no_di.md](docs/di_vs_no_di.md).
- **REST Level 2** — correct verbs + status codes.
- **RFC 7807** — `app/core/problems.py`.
- **Idempotency** — `Idempotency-Key` on register (`app/services/enrollment.py`).
- **API versioning** — path-based under `/api/v1`.
- **Registration transaction** — row lock + capacity + window + clash checks; see [docs/design_notes.md](docs/design_notes.md).

## Local dev / tests (needs `uv`)

```bash
make test    # pytest on in-memory SQLite (no Postgres) — unit + integration
make lint    # ruff + mypy
make dev     # uvicorn --reload (needs a reachable Postgres)
```
Config is environment-driven (`APP_*`); copy `.env.example` → `.env` for local runs.
