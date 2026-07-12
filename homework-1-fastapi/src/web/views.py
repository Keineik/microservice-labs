"""View-model builders shared between page routes and HTMX action routes.

The registration screen has one HTMX-swappable region (``#register-content``)
driven by a single partial. Search, the open-only toggle, pagination, register,
and drop all re-render that region — so they all need the same context. Building
it in one place keeps those paths consistent.
"""

import math
from typing import Any

from web.academics import find_clash
from web.api_client import ApiClient

Ctx = dict[str, Any]


async def build_register_context(
    api: ApiClient,
    *,
    student: Ctx,
    term: Ctx | None,
    search: str | None,
    open_only: bool,
    page: int,
    size: int,
    flash: Ctx | None = None,
) -> Ctx:
    """Everything the registration partial needs: the offerings page, the
    student's current selections for this term, and per-row derived state
    (already-registered / full / schedule clash)."""
    if term is None:
        return {
            "term": None,
            "offerings": [],
            "page": 1,
            "pages": 1,
            "total": 0,
            "search": search or "",
            "open_only": open_only,
            "registrations": [],
            "selected_credits": 0,
            "term_open": False,
            "flash": flash,
        }

    term_id = term["id"]

    offerings_page = await api.get(
        "/offerings",
        params={
            "term_id": term_id,
            "open_only": open_only,
            "search": search,
            "page": page,
            "size": size,
        },
    )

    registrations = await api.get(
        f"/students/{student['id']}/enrollments",
        params={"status": "REGISTERED", "term_id": term_id},
    )
    registered_offerings = [r["offering"] for r in registrations]
    enrollment_by_offering = {r["offering_id"]: r for r in registrations}

    rows: list[Ctx] = []
    for offering in offerings_page["items"]:
        enrollment = enrollment_by_offering.get(offering["id"])
        clash = None if enrollment else find_clash(offering, registered_offerings)
        rows.append(
            {
                "offering": offering,
                "enrollment": enrollment,  # set => student is registered
                "is_full": offering["available_seats"] <= 0,
                "clash": clash,  # a clashing offering dict, or None
            }
        )

    total = offerings_page["total"]
    pages = max(1, math.ceil(total / size)) if size else 1

    return {
        "term": term,
        "offerings": rows,
        "page": offerings_page["page"],
        "pages": pages,
        "total": total,
        "search": search or "",
        "open_only": open_only,
        "registrations": registrations,
        "selected_credits": sum(r["offering"]["course"]["credits"] for r in registrations),
        "term_open": term["is_registration_open"],
        "flash": flash,
    }
