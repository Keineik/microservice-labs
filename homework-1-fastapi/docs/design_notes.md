# Design notes (for the report)

## Domain model — why offerings and terms

A naive model puts `semester` directly on the enrollment, which wrongly implies
every course is always registrable. Real systems separate:

- **Course** — the catalog entry (what the course *is*): code, title, credits.
- **Term** — a semester/year *with a registration window* (`registration_starts_at`
  / `registration_ends_at`): when the school lets students register.
- **CourseOffering** — a Course *opened* in a Term: a section with its own
  **capacity**, **schedule** (day/time/room), instructor, and status. This is the
  concrete thing a student registers for. Not every course is offered every term.
- **Enrollment** — Student ↔ Offering, with `status`
  (REGISTERED → DROPPED | COMPLETED) and `grade`.

This is why `semester` is no longer on the enrollment: the offering already knows
its term. It also enables the BT3 web app: **past courses & scores** are
`COMPLETED` enrollments (with grades) in past terms; **current registrations** are
`REGISTERED` in the open term; **browse to register** lists offerings in the open
term.

## Registration rules & transaction safety

`POST /enrollments` runs one transaction that, in order:
1. locks the offering row (`SELECT … FOR UPDATE`) so concurrent registrations
   can't overbook the same section;
2. checks the offering is `OPEN` and the **term registration window is open**;
3. rejects a duplicate active registration (also backed by a **partial unique
   index** on `(student_id, offering_id) WHERE status='REGISTERED'`);
4. checks **capacity** (`active REGISTERED < capacity`) under the row lock;
5. checks for a **weekly schedule clash** with the student's other registrations
   that term;
6. inserts the enrollment and (if an `Idempotency-Key` was sent) records it so a
   retry is safe.

`DELETE /enrollments/{id}` cancels (soft `DROPPED`) — allowed only while the
term's registration window is still open, which frees the seat.

## BT3 web client (`src/web/`)

The web app is a **separate FastAPI service** that renders HTML with Jinja2 +
HTMX and talks to the JSON API over HTTP (`httpx`). It has **no database access**
of its own. The request path is `browser → web (BFF) → API → DB`, which is a
deliberate, honest client/server split for the distributed-systems course rather
than folding the UI into the API process. The JSON API is unchanged, so its tests
and contract are unaffected.

- **Server-rendered + HTMX, minimal JS.** Search, pagination, register, and drop
  are HTMX requests that swap an HTML fragment; there is essentially no
  hand-written JavaScript and no front-end build step.
- **Login simulation.** Consistent with "no auth yet", the acting student is held
  in a cookie and chosen via the top-right **profile switcher** (searchable). This
  stands in for a login/session — a real system would derive the student from the
  authenticated principal and authorize every call.
- **Derived academic figures (GPA, credits).** Cumulative/per-term GPA
  (credit-weighted, 0–10 scale) and credit totals are computed in the web layer
  (`src/web/academics.py`) from the enrollment records the API returns. This is a
  presentation-time aggregation; a production system would more likely expose a
  `GET /students/{id}/academic-summary` endpoint so that domain logic lives in the
  API service. Kept web-side here to leave the API surface untouched.
- **Filter placement.** Offering search/pagination are **server-side** (the API
  already does `ilike` + paging, and a term can have many sections). The transcript
  term filter is also routed through the API for consistency, though a single
  student's enrollment set is small enough that client-side filtering would work
  too.
- **Schedule-clash warnings** are recomputed in the UI (mirroring the server rule)
  only to warn *before* submitting; the API remains the source of truth and still
  returns a 409 on a real clash.

## Scope & assumptions (please note)

- **No authentication yet.** Auth/authorization is intentionally out of scope for
  this exercise (it is planned for a later assignment). Until then the API takes
  the acting `student_id` explicitly rather than deriving it from a session/token.
  In a real system every `/students/{id}/…` and registration call would be
  authorized against the logged-in user.
- **Admin operations are out of scope.** Managing the catalog (creating courses,
  terms, offerings) and adding/removing students are *not* exposed as endpoints;
  those tables are populated by the seed script. The API surface is limited to
  **student-facing activities**: browse the catalog/offerings, view your own
  enrollments and schedule, register, and cancel.
- **Terms is a small dimension table** (a handful of rows); the "≥100 rows"
  guidance is met by students, courses, offerings, and enrollments.
- **Concurrency note:** the `FOR UPDATE` lock is exercised on Postgres. The test
  suite runs on SQLite (single-threaded), where row locking is a no-op — the
  logic is present and correct, but true concurrency is only meaningful against
  Postgres.
