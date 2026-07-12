from fastapi import APIRouter

from app.api.v2.routes import students

# The v2 aggregate router, mounted under /api/v2 (sibling to v1). For this
# homework only the `students` resource is re-versioned, to demonstrate that a
# breaking contract change can ship as v2 while v1 keeps serving old clients
# unchanged. A real migration would re-version every resource (or fall back to
# v1 for unchanged ones).
api_router = APIRouter()
api_router.include_router(students.router)
