from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from redis import Redis

from app.core.config import settings
from app.core.logger import auth_logger, db_logger
from app.core.security import get_current_active_user, get_current_user
from app.db.session import get_db as get_db_session
from app.models.user import User


# Redis connection
def get_redis() -> Redis:
    """Get Redis client"""
    try:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=settings.REDIS_DECODE_RESPONSES,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT
        )
        return redis_client
    except Exception as e:
        auth_logger.error(f"Redis connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis connection failed"
        )


# Database session dependency
def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    try:
        db = get_db_session()
        yield db
    finally:
        try:
            db.close()
        except Exception as e:
            db_logger.error(f"Database session close error: {str(e)}")


# Current user dependency (cached for multiple calls in same request)
async def get_current_user_cached(
    user: User = Depends(get_current_user)
) -> User:
    """Get current user (returns same instance for same request)"""
    return user


# Current active user dependency
async def get_current_active_user_cached(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current active user (returns same instance for same request)"""
    return current_user


# Current admin dependency
async def get_current_admin_user_cached(
    current_user: User = Depends(get_current_admin_user)
) -> User:
    """Get current admin user (returns same instance for same request)"""
    return current_user


# Security utilities
def require_token(token: str = Depends(oauth2_scheme)):
    """Require Bearer token for authentication"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    return token


# Rate limiting dependency (basic implementation)
def check_rate_limit(
    user_id: Optional[str] = None,
    redis: Redis = Depends(get_redis)
):
    """Basic rate limiting check"""
    if not settings.RATE_LIMIT_ENABLED:
        return

    # Check current rate
    key = f"rate_limit:{user_id or 'anonymous'}"
    current_count = redis.get(key)

    if current_count is None:
        redis.setex(
            key,
            settings.RATE_LIMIT_PERIOD,
            1
        )
    else:
        count = int(current_count) + 1
        if count > settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )
        redis.set(key, count)