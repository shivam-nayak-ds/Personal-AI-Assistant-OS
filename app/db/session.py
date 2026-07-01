from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import os

# Get database URL from environment or use default
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # Use the default from config but replace password if in env
    if os.getenv("POSTGRES_PASSWORD"):
        DATABASE_URL = f"postgresql://postgres:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/hermes_ai"
    else:
        DATABASE_URL = "postgresql://postgres:password@localhost:5432/hermes_ai"

# Get async database URL
DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Sync Database Engine
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("DB_POOL_SIZE", 20)),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 10)),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", 30)),
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 3600)),
    echo=settings.DEBUG
)

# Async Database Engine
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=settings.DEBUG
)

# Session Local - For Sync Database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Session Local - For Async Database
AsyncSessionLocal = sessionmaker(autoflush=False, bind=async_engine, class_=AsyncSession)


def get_db():
    """FastAPI dependency for sync DB sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """FastAPI dependency for async DB sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def init_db():
    """Initialize the database with all tables"""
    from app.db.base import Base  # ✅ Base import fix
    from app.models.user import User
    from app.models.goal import Goal
    from app.models.task import Task

    Base.metadata.create_all(bind=engine)


def close_db():
    """Close sync database session"""
    try:
        engine.dispose()
    except Exception:
        pass


async def close_async_db():
    """Close async database session"""
    try:
        await async_engine.dispose()
    except Exception:
        pass


def check_database_health() -> bool:
    """Returns True if DB is healthy"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # ✅ SQLAlchemy 2.x fix
        return True
    except Exception:
        return False
    finally:
        try:
            db.close()
        except Exception:
            pass


async def check_async_database_health() -> bool:
    """Returns True if async DB is healthy"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))  # ✅ SQLAlchemy 2.x fix
        return True
    except Exception:
        return False


def get_pool_stats() -> dict:
    """Returns connection pool statistics"""
    pool = engine.pool
    return {
        "pool_size": int(pool.size()),
        "max_overflow": int(pool._max_overflow),
        "overflow": int(pool.overflow())
    }