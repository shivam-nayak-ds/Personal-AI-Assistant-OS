"""
Database session management with SQLAlchemy.

Features:
- Connection pooling (20 connections + 10 overflow)
- Async support with asyncpg
- Session lifecycle management
- Automatic cleanup
- Health check utilities
"""

from typing import Generator
from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


# ============== Sync Database Engine ==============

# Create synchronous engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session factory for sync operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)


# ============== Async Database Engine ==============

# Create async engine (for FastAPI async endpoints)
async_engine = create_async_engine(
    settings.database_url_async,  # postgresql+asyncpg://...
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factory for async operations
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ============== Session Dependencies ==============

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for synchronous database sessions.
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


async def get_async_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency for asynchronous database sessions.
    
    Usage in FastAPI:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
    
    Yields:
        AsyncSession: Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Async database session created")
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {str(e)}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Async database session closed")


# ============== Connection Pool Events ==============

@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when new connection is created."""
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when connection is checked out from pool."""
    logger.debug("Connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when connection is returned to pool."""
    logger.debug("Connection returned to pool")


# ============== Health Check ==============

def check_database_health() -> bool:
    """
    Check if database is healthy and accepting connections.
    
    Returns:
        bool: True if database is healthy
    """
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        logger.info("Database health check: OK")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return False


async def check_async_database_health() -> bool:
    """
    Check if async database is healthy.
    
    Returns:
        bool: True if database is healthy
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        logger.info("Async database health check: OK")
        return True
    except Exception as e:
        logger.error(f"Async database health check failed: {str(e)}", exc_info=True)
        return False


# ============== Connection Pool Stats ==============

def get_pool_stats() -> dict:
    """
    Get current connection pool statistics.
    
    Returns:
        dict: Pool statistics
    """
    pool_obj = engine.pool
    return {
        "pool_size": pool_obj.size(),
        "checked_in": pool_obj.checkedin(),
        "checked_out": pool_obj.checkedout(),
        "overflow": pool_obj.overflow(),
        "total_connections": pool_obj.size() + pool_obj.overflow(),
    }


# ============== Startup/Shutdown ==============

def init_db():
    """
    Initialize database connection pool on startup.
    Call this in FastAPI startup event.
    """
    logger.info(
        "Initializing database connection pool",
        extra={
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "database_url": settings.DATABASE_URL.split("@")[1],  # Hide credentials
        }
    )
    
    # Test connection
    if check_database_health():
        logger.info("Database connection pool initialized successfully")
    else:
        logger.error("Failed to initialize database connection pool")
        raise Exception("Database connection failed")


def close_db():
    """
    Close database connection pool on shutdown.
    Call this in FastAPI shutdown event.
    """
    logger.info("Closing database connection pool")
    engine.dispose()
    logger.info("Database connection pool closed")


async def close_async_db():
    """
    Close async database connection pool on shutdown.
    """
    logger.info("Closing async database connection pool")
    await async_engine.dispose()
    logger.info("Async database connection pool closed")


# Example usage:
"""
# In FastAPI app (main.py)

from app.db.session import init_db, close_db, get_db, get_async_db

@app.on_event("startup")
async def startup_event():
    init_db()

@app.on_event("shutdown")
async def shutdown_event():
    close_db()
    await close_async_db()

# Sync endpoint
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Async endpoint
@app.get("/users-async")
async def get_users_async(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Health check endpoint
@app.get("/health")
async def health_check():
    db_healthy = check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": db_healthy,
        "pool_stats": get_pool_stats()
    }
"""
