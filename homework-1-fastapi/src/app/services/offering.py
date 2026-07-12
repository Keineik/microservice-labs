from app.core.problems import NotFoundError
from app.models import CourseOffering
from app.repositories.offering import OfferingRepository


class OfferingService:
    def __init__(self, repo: OfferingRepository) -> None:
        self.repo = repo

    async def get(self, offering_id: int) -> CourseOffering:
        offering = await self.repo.get_detail(offering_id)
        if offering is None:
            raise NotFoundError(f"Offering {offering_id} does not exist")
        return offering

    async def list(
        self,
        *,
        term_id: int | None,
        course_id: int | None,
        search: str | None,
        open_only: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[CourseOffering], int]:
        return await self.repo.list(
            term_id=term_id,
            course_id=course_id,
            search=search,
            open_only=open_only,
            offset=offset,
            limit=limit,
        )
