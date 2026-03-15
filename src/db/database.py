"""
Database configuration and initialization
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path

# Database path
DB_PATH = Path(__file__).resolve().parent / "bryt.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


async def init_db():
    """Initialize database tables"""
    from . import models  # Import models to register them
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session

