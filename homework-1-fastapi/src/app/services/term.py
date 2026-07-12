from app.core.problems import NotFoundError
from app.models import Term
from app.repositories.term import TermRepository


class TermService:
    def __init__(self, repo: TermRepository) -> None:
        self.repo = repo

    async def get(self, term_id: int) -> Term:
        term = await self.repo.get(term_id)
        if term is None:
            raise NotFoundError(f"Term {term_id} does not exist")
        return term

    async def list(self) -> list[Term]:
        return await self.repo.list()
