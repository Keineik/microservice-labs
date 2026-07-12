from fastapi import APIRouter, Depends

from app.api.deps import get_term_service
from app.schemas.common import Problem
from app.schemas.term import TermOut
from app.services.term import TermService

router = APIRouter(prefix="/terms", tags=["terms"])


@router.get("", response_model=list[TermOut], summary="List terms (with registration window)")
async def list_terms(service: TermService = Depends(get_term_service)) -> list[TermOut]:
    return [TermOut.model_validate(t) for t in await service.list()]


@router.get(
    "/{term_id}",
    response_model=TermOut,
    responses={404: {"model": Problem}},
    summary="Get a term by id",
)
async def get_term(term_id: int, service: TermService = Depends(get_term_service)) -> TermOut:
    return TermOut.model_validate(await service.get(term_id))
