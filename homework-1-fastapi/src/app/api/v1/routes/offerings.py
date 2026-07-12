from fastapi import APIRouter, Depends, Query

from app.api.deps import Pagination, get_offering_service
from app.schemas.common import Page, Problem
from app.schemas.offering import OfferingOut
from app.services.offering import OfferingService

router = APIRouter(prefix="/offerings", tags=["offerings"])


@router.get(
    "",
    response_model=Page[OfferingOut],
    summary="Browse course offerings (sections) — filter by term/course, search, open-only",
)
async def list_offerings(
    term_id: int | None = Query(None, description="filter to one term"),
    course_id: int | None = Query(None, description="filter to one course"),
    search: str | None = Query(None, description="match on course title / code"),
    open_only: bool = Query(False, description="only offerings with status OPEN"),
    pagination: Pagination = Depends(),
    service: OfferingService = Depends(get_offering_service),
) -> Page[OfferingOut]:
    items, total = await service.list(
        term_id=term_id,
        course_id=course_id,
        search=search,
        open_only=open_only,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return Page[OfferingOut](
        items=[OfferingOut.model_validate(o) for o in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
    )


@router.get(
    "/{offering_id}",
    response_model=OfferingOut,
    responses={404: {"model": Problem}},
    summary="Get an offering (seats + schedule + registration status)",
)
async def get_offering(
    offering_id: int, service: OfferingService = Depends(get_offering_service)
) -> OfferingOut:
    return OfferingOut.model_validate(await service.get(offering_id))
