"""Request-scoped dependencies: the API client, the 'logged-in' student, and
the current (registration-open) term."""

from typing import Any

from fastapi import Depends, Request

from web.api_client import ApiClient, ApiError
from web.config import get_web_settings

COOKIE_STUDENT = "student_id"

Student = dict[str, Any]
Term = dict[str, Any]


def get_client(request: Request) -> ApiClient:
    """The shared httpx-backed client, created once in the app lifespan."""
    client: ApiClient = request.app.state.api
    return client


async def get_current_student(request: Request, api: ApiClient = Depends(get_client)) -> Student:
    """Resolve the 'logged-in' student from the cookie (auth is out of scope).

    Falls back to the configured default student if the cookie is missing or
    points at a student the API can't find.
    """
    settings = get_web_settings()
    raw = request.cookies.get(COOKIE_STUDENT)
    student_id = int(raw) if raw and raw.isdigit() else settings.default_student_id
    try:
        return await api.get(f"/students/{student_id}")
    except ApiError:
        return await api.get(f"/students/{settings.default_student_id}")


async def get_current_term(api: ApiClient = Depends(get_client)) -> Term | None:
    """The term students register into: the one whose registration window is
    open. If none is open, fall back to the most recent term so the read-only
    screens still show something."""
    terms: list[Term] = await api.get("/terms")
    if not terms:
        return None
    open_terms = [t for t in terms if t["is_registration_open"]]
    if open_terms:
        return open_terms[0]
    return max(terms, key=lambda t: t["starts_on"])
