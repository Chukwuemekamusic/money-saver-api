from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from functools import lru_cache

from app.core.config import get_settings

settings = get_settings()


# SQLAlchemy Base
class Base(DeclarativeBase):
    pass


# Database engine
@lru_cache()
def get_engine():
    """Create async database engine"""
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    database_url = settings.DATABASE_URL
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        pool_pre_ping=True,
    )


# Session factory
async_session_factory = async_sessionmaker(
    get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all database tables"""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def health_check_db() -> bool:
    """Check if database connection is healthy"""
    try:
        async with async_session_factory() as session:
            # Simple query to test connection
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False