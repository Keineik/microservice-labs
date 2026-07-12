from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdempotencyKey


class IdempotencyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, key: str) -> IdempotencyKey | None:
        res = await self.db.execute(select(IdempotencyKey).where(IdempotencyKey.key == key))
        return res.scalar_one_or_none()

    async def add(
        self, *, key: str, method: str, path: str, status_code: int, resource_id: int
    ) -> IdempotencyKey:
        record = IdempotencyKey(
            key=key, method=method, path=path, status_code=status_code, resource_id=resource_id
        )
        self.db.add(record)
        await self.db.flush()
        return record
