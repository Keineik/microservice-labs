from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    echo=_settings.db_echo,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yield one session per request, always closed.

    This is the seam that makes the whole app testable — tests override this
    single provider (``app.dependency_overrides[get_db]``) to point at a
    throwaway database, and every layer above it is unchanged.
    """
    async with SessionLocal() as session:
        yield session
