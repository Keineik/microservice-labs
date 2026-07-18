# Dependency Injection: with vs. without

This service uses FastAPI's built-in DI (`Depends`). Here is the contrast between
using it and not.

## Without DI (anti-pattern)

The handler reaches for globals and builds its own collaborators:

```python
# global, shared engine/session
session = SessionLocal()

@app.post("/students")
async def create_student(payload: dict):
    # business logic + data access mashed into the route
    existing = await session.execute(
        select(Student).where(Student.student_code == payload["student_code"])
    )
    if existing.scalar_one_or_none():
        return JSONResponse({"error": "dup"}, status_code=409)
    student = Student(**payload)
    session.add(student)
    await session.commit()
    return student
```

Problems:
- **Not testable in isolation** — you can't run this without a real database;
  the session is a hard-wired global.
- **Wrong lifecycle** — one shared session across all requests invites leaked
  state and concurrency bugs; nothing guarantees close/rollback.
- **Tight coupling** — route knows about querying, the ORM, and commit; you
  cannot swap the data source or reuse the logic elsewhere.

## With DI (this project)

Providers declare *what* a handler needs; FastAPI supplies it per request:

```python
# app/api/deps.py
def get_student_repo(db: AsyncSession = Depends(get_db)) -> StudentRepository:
    return StudentRepository(db)

def get_student_service(
    db: AsyncSession = Depends(get_db),
    repo: StudentRepository = Depends(get_student_repo),
) -> StudentService:
    return StudentService(db, repo)

# route
@router.post("", status_code=201)
async def create_student(payload: StudentCreate,
                         service: StudentService = Depends(get_student_service)):
    return StudentOut.model_validate(await service.create(payload))
```

Benefits observed here:

| Concern | Without DI | With DI |
|---|---|---|
| Testability | needs a real DB | override `get_db` → in-memory SQLite (`tests/conftest.py`) |
| Session lifecycle | manual/global | per-request, auto-closed by `get_db`'s generator |
| Coupling | route ↔ ORM ↔ commit | route → service → repository (swap any layer) |
| Reuse | copy/paste | one service used by many routes |

## The proof is in the tests

- `tests/unit/test_student_service.py` runs the **real service** against a
  **fake repository/session** — no DB, no HTTP — because the service's
  dependencies are injected.
- `tests/integration/test_api.py` runs the **whole app** against a throwaway
  database by overriding exactly one provider (`get_db`).

Neither is possible cleanly without DI.
