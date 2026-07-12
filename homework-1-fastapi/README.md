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
make up      # build + start postgres, api, and the web client; migrations run on startup
make seed    # 150 students, 100 courses, 3 terms, 150 offerings, ~1.6k enrollments
```
API Swagger UI → http://localhost:8000/docs · health → `/health`
**Web app (BT3)** → http://localhost:8001 (run `make seed` first if the DB is empty)

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

## Web client (BT3) — `src/web/`

A **server-rendered** UI (Jinja2 + [HTMX](https://htmx.org/)) that lets a student
browse offerings, register/cancel, and view their transcript and weekly schedule.
It is a **separate FastAPI service** that consumes the JSON API over HTTP
(`httpx`) — it never touches the database. This keeps a clean browser → web/BFF →
API → DB split (fitting for the distributed-systems course) and leaves the JSON
API untouched. Nearly zero hand-written JS: HTMX swaps HTML fragments for search,
pagination, register, and drop.

| Screen | Route | What it shows |
|---|---|---|
| Dashboard | `/` | cumulative GPA, credits earned / in progress, registration-window status, current registrations |
| Register | `/register` | browse the open term's offerings (server-side search + pagination), a "my selections" cart, register/drop with live seat/credit updates and clash warnings |
| My Courses | `/transcript` | past courses grouped by term with grades + per-term & cumulative GPA; term filter |
| Schedule | `/schedule` | weekly timetable grid of the current term's registered classes |

> **Login is out of scope** (same note as the API). "Who is logged in" is
> simulated by the **profile switcher** (top-right) — search any student and
> switch; the choice is kept in a cookie. See [docs/design_notes.md](docs/design_notes.md).

Run just the web client locally (against an API already on `:8000`): `make web`.

## How each requirement is met

- **Contract + Swagger** — Pydantic schemas → `/docs`, `/redoc`, `/openapi.json`.
- **≥3 related tables, 100+ rows** — students/courses/offerings/enrollments (see `make seed`).
- **DI** — FastAPI `Depends` (`app/api/deps.py`) + [docs/di_vs_no_di.md](docs/di_vs_no_di.md).
- **REST Level 2** — correct verbs + status codes.
- **RFC 7807** — `app/core/problems.py`.
- **Idempotency** — `Idempotency-Key` on register (`app/services/enrollment.py`).
- **API versioning** — path-based: `/api/v1` and `/api/v2` served side by side.
  `/api/v2/students` ships a **breaking** contract change (`student_code`→`code`,
  `full_name`→`name`, timestamps dropped) while v1 stays unchanged — demonstrating
  non-breaking evolution. Both reuse the same service/repo layer. **Demo:**
  ```bash
  curl -s localhost:8000/api/v1/students/1   # {"student_code":"SV00001","full_name":"…", "created_at":…}
  curl -s localhost:8000/api/v2/students/1   # {"code":"SV00001","name":"…"}  (no timestamps)
  ```
  Both also appear in `/docs`, tagged `students` and `students (v2)`.
- **Registration transaction** — row lock + capacity + window + clash checks; see [docs/design_notes.md](docs/design_notes.md).

## Local dev / tests (needs `uv`)

```bash
make test    # pytest on in-memory SQLite (no Postgres) — unit + integration
make lint    # ruff + mypy
make dev     # uvicorn --reload (needs a reachable Postgres)
```
Config is environment-driven (`APP_*`); copy `.env.example` → `.env` for local runs.
