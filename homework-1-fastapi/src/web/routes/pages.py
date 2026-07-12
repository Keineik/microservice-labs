"""Full-page (and read-only HTMX partial) routes.

Register/drop write actions live in ``actions.py``. Everything here is a GET.
"""

from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web import academics
from web.api_client import ApiClient
from web.config import get_web_settings
from web.deps import COOKIE_STUDENT, get_client, get_current_student, get_current_term
from web.templating import templates
from web.views import build_register_context

router = APIRouter()

Ctx = dict[str, Any]


def _days_left(iso_dt: str) -> int:
    """Whole days from now until an ISO datetime (negative if past)."""
    end = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    if end.tzinfo is None:
        end = end.replace(tzinfo=UTC)
    return (end - datetime.now(UTC)).days


# --- Dashboard ------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    enrollments = await api.get(f"/students/{student['id']}/enrollments")
    current = [e for e in enrollments if e["status"] == "REGISTERED"]

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "active": "dashboard",
            "student": student,
            "term": term,
            "gpa": academics.cumulative_gpa(enrollments),
            "credits_earned": academics.credits_earned(enrollments),
            "credits_in_progress": academics.credits_in_progress(enrollments),
            "completed_count": sum(1 for e in enrollments if e["status"] == "COMPLETED"),
            "current": current,
            "days_left": _days_left(term["registration_ends_at"]) if term else None,
        },
    )


# --- Register (browse offerings) ------------------------------------------
@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    search: str | None = Query(None),
    open_only: bool = Query(True),
    page: int = Query(1, ge=1),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    ctx = await build_register_context(
        api,
        student=student,
        term=term,
        search=search,
        open_only=open_only,
        page=page,
        size=get_web_settings().offerings_page_size,
    )
    return templates.TemplateResponse(
        request, "register.html", {"active": "register", "student": student, **ctx}
    )


@router.get("/register/content", response_class=HTMLResponse)
async def register_content(
    request: Request,
    search: str | None = Query(None),
    open_only: bool = Query(True),
    page: int = Query(1, ge=1),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    """HTMX partial: re-renders #register-content for search/toggle/pagination."""
    ctx = await build_register_context(
        api,
        student=student,
        term=term,
        search=search,
        open_only=open_only,
        page=page,
        size=get_web_settings().offerings_page_size,
    )
    return templates.TemplateResponse(
        request, "_register_content.html", {"student": student, **ctx}
    )


# --- My Courses (transcript) ----------------------------------------------
@router.get("/transcript", response_class=HTMLResponse)
async def transcript_page(
    request: Request,
    term_id: int | None = Query(None),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
) -> HTMLResponse:
    enrollments = await api.get(f"/students/{student['id']}/enrollments")
    terms = academics.completed_by_term(enrollments)
    shown = [g for g in terms if term_id is None or g["term"]["id"] == term_id]

    return templates.TemplateResponse(
        request,
        "transcript.html",
        {
            "active": "transcript",
            "student": student,
            "gpa": academics.cumulative_gpa(enrollments),
            "credits_earned": academics.credits_earned(enrollments),
            "credits_in_progress": academics.credits_in_progress(enrollments),
            "term_groups": shown,
            "all_terms": [g["term"] for g in terms],
            "selected_term_id": term_id,
        },
    )


@router.get("/transcript/list", response_class=HTMLResponse)
async def transcript_list(
    request: Request,
    term_id: int | None = Query(None),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
) -> HTMLResponse:
    """HTMX partial: term-filtered transcript list (the API does the filtering
    when a term is chosen)."""
    enrollments = await api.get(f"/students/{student['id']}/enrollments")
    groups = academics.completed_by_term(enrollments)
    shown = [g for g in groups if term_id is None or g["term"]["id"] == term_id]
    return templates.TemplateResponse(request, "_transcript_list.html", {"term_groups": shown})


# --- Weekly schedule ------------------------------------------------------
@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(
    request: Request,
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    items: list[Ctx] = []
    if term is not None:
        items = await api.get(f"/students/{student['id']}/schedule", params={"term_id": term["id"]})

    days = ["MON", "TUE", "WED", "THU", "FRI"]
    # Rows = the distinct start times actually in this schedule, sorted.
    slots = sorted({i["start_time"] for i in items})
    grid: dict[tuple[str, str], Ctx] = {(i["day_of_week"], i["start_time"]): i for i in items}

    return templates.TemplateResponse(
        request,
        "schedule.html",
        {
            "active": "schedule",
            "student": student,
            "term": term,
            "items": items,
            "days": days,
            "slots": slots,
            "grid": grid,
            "total_credits": None,  # schedule endpoint doesn't carry credits
        },
    )


# --- Student switcher (login simulation) ----------------------------------
@router.get("/students/search", response_class=HTMLResponse)
async def students_search(
    request: Request,
    q: str | None = Query(None),
    api: ApiClient = Depends(get_client),
) -> HTMLResponse:
    """HTMX partial: live student search for the top-right profile switcher."""
    result = await api.get("/students", params={"search": q, "size": 8})
    # Return to whatever page the user is currently on after switching.
    current_url = request.headers.get("HX-Current-URL", "/")
    next_path = urlparse(current_url).path or "/"
    return templates.TemplateResponse(
        request,
        "_switcher_results.html",
        {"students": result["items"], "next_path": next_path},
    )


@router.get("/switch/{student_id}")
async def switch_student(student_id: int, next: str = "/") -> RedirectResponse:
    """Set the 'logged-in' student cookie and bounce back. Auth is out of scope;
    this simulates picking a session identity."""
    target = next if next.startswith("/") else "/"
    response = RedirectResponse(url=target, status_code=303)
    response.set_cookie(COOKIE_STUDENT, str(student_id), path="/", max_age=60 * 60 * 24 * 7)
    return response
