"""
Database package for Hermes AI OS.

Exports:
- Base: Base class for all models
- get_db: Dependency for sync database sessions
- get_async_db: Dependency for async database sessions
- engine: SQLAlchemy engine
- async_engine: Async SQLAlchemy engine
"""

from app.db.base import Base
from app.db.session import (
    get_db,
    get_async_db,
    engine,
    async_engine,
    init_db,
    close_db,
    close_async_db,
    check_database_health,
    check_async_database_health,
    get_pool_stats,
)

__all__ = [
    "Base",
    "get_db",
    "get_async_db",
    "engine",
    "async_engine",
    "init_db",
    "close_db",
    "close_async_db",
    "check_database_health",
    "check_async_database_health",
    "get_pool_stats",
]
