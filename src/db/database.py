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
    """Initialize database tables and seed default admin user"""
    from . import models  # Import models to register them
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy import select
    from .models import AdminUser
    async with async_session() as session:
        existing = (await session.execute(
            select(AdminUser).where(AdminUser.username == "admin")
        )).scalar_one_or_none()
        if not existing:
            session.add(AdminUser(
                username="admin",
                password_hash="$2b$12$XYiGK07pb5FUbDHXoZgjDeJ.TX9/7d8A72SX4COiWnq/.L1UAQnGm"
            ))
            await session.commit()


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session

