from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from contextlib import asynccontextmanager

from .models import Base

# Create async engine
engine = create_async_engine(
    "sqlite+aiosqlite:///bot/database/shop.db",
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600  # Recycle connections after 1 hour
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """Close all connections and dispose of the engine"""
    await engine.dispose()

@asynccontextmanager
async def get_session():
    """Provide a transactional scope around a series of operations."""
    session = async_session()
    try:
        yield session
    finally:
        await session.close()