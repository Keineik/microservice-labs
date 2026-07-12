from fastapi import APIRouter

from app.api.v1.routes import courses, enrollments, students

# The v1 aggregate router. main.py mounts this under settings.api_v1_prefix
# (/api/v1). A future v2 would be a sibling package mounted under /api/v2 —
# that is the whole idea of path-based API versioning.
api_router = APIRouter()
api_router.include_router(students.router)
api_router.include_router(courses.router)
api_router.include_router(enrollments.router)
