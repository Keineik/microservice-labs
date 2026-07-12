"""HTMX write actions: register for an offering, drop a registration.

Both re-render the whole ``#register-content`` region (via ``_register_content``)
so seats, the 'my selections' panel, and the credit total all update together.
The current filter/page state is carried on the request URL so the re-render
lands on the same view. API errors (full / clash / closed / duplicate) come
back as an inline flash.
"""

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from web.api_client import ApiClient, ApiError
from web.config import get_web_settings
from web.deps import get_client, get_current_student, get_current_term
from web.templating import templates
from web.views import build_register_context

router = APIRouter()

Ctx = dict[str, Any]


async def _render_register(
    request: Request,
    api: ApiClient,
    student: Ctx,
    term: Ctx | None,
    search: str | None,
    open_only: bool,
    page: int,
    flash: Ctx,
) -> HTMLResponse:
    ctx = await build_register_context(
        api,
        student=student,
        term=term,
        search=search,
        open_only=open_only,
        page=page,
        size=get_web_settings().offerings_page_size,
        flash=flash,
    )
    return templates.TemplateResponse(
        request, "_register_content.html", {"student": student, **ctx}
    )


@router.post("/register/{offering_id}", response_class=HTMLResponse)
async def register_offering(
    offering_id: int,
    request: Request,
    search: str | None = Query(None),
    open_only: bool = Query(True),
    page: int = Query(1, ge=1),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    try:
        await api.post(
            "/enrollments",
            json={"student_id": student["id"], "offering_id": offering_id},
            # A fresh idempotency key per click: a double-submit (or HTMX retry)
            # replays the same registration instead of erroring.
            headers={"Idempotency-Key": str(uuid4())},
        )
        flash: Ctx = {"type": "success", "message": "Registered successfully."}
    except ApiError as exc:
        flash = {"type": "error", "message": exc.message}
    return await _render_register(request, api, student, term, search, open_only, page, flash)


@router.post("/drop/{enrollment_id}", response_class=HTMLResponse)
async def drop_enrollment(
    enrollment_id: int,
    request: Request,
    search: str | None = Query(None),
    open_only: bool = Query(True),
    page: int = Query(1, ge=1),
    api: ApiClient = Depends(get_client),
    student: Ctx = Depends(get_current_student),
    term: Ctx | None = Depends(get_current_term),
) -> HTMLResponse:
    try:
        await api.delete(f"/enrollments/{enrollment_id}")
        flash: Ctx = {"type": "success", "message": "Dropped the course."}
    except ApiError as exc:
        flash = {"type": "error", "message": exc.message}
    return await _render_register(request, api, student, term, search, open_only, page, flash)
