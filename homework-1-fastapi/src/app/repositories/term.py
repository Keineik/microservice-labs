from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Term


class TermRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, term_id: int) -> Term | None:
        return await self.db.get(Term, term_id)

    async def list(self) -> list[Term]:
        rows = (await self.db.execute(select(Term).order_by(Term.code))).scalars().all()
        return list(rows)
