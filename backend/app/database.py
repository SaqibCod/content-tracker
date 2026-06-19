from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models.

    Exposed via ``app.models`` so Alembic can target ``Base.metadata``.
    """


# Async engine + session factory. ``expire_on_commit=False`` keeps attributes
# accessible after commit so we can serialize a row without an extra refresh.
engine = create_async_engine(settings.database_url, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped async session."""
    async with AsyncSessionLocal() as session:
        yield session
