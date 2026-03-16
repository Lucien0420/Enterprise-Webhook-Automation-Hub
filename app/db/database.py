"""Database connection and session management."""
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.order import Base

db_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")

# Ensure data/ exists for SQLite file path (e.g. ./data/webhook_orders.db)
if "sqlite" in db_url and "/" in db_url.split("///")[-1]:
    db_path = Path(db_url.split("///")[-1])
    if db_path.suffix == ".db":
        db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(db_url, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yield DB session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
