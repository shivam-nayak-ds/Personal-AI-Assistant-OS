"""
Redis Client for Hermes AI OS

Features:
- Connection pooling
- Key namespacing (hermes:*)
- TTL management
- JSON serialization
- Health check
"""

import json
from typing import Any, Optional
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Key prefix for all Hermes keys
KEY_PREFIX = "hermes"


class RedisClient:
    """
    Async Redis client with namespacing and JSON support.

    Usage:
        redis = RedisClient()
        await redis.set("user:123", {"name": "Shivam"}, ttl=3600)
        data = await redis.get("user:123")
    """

    def __init__(self):
        self._client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Initialize Redis connection pool"""
        try:
            self._client = await aioredis.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            )
            # Test connection
            await self._client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection"""
        if self._client:
            await self._client.aclose()
            logger.info("Redis connection closed")

    def _make_key(self, key: str) -> str:
        """Add namespace prefix to key"""
        return f"{KEY_PREFIX}:{key}"

    # ─────────────────────────────────────────
    # CORE OPERATIONS
    # ─────────────────────────────────────────

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in Redis (auto JSON serialize).

        Args:
            key: Cache key
            value: Any JSON-serializable value
            ttl: Time-to-live in seconds (None = no expiry)
        """
        try:
            full_key = self._make_key(key)
            serialized = json.dumps(value)

            if ttl:
                await self._client.setex(full_key, ttl, serialized)
            else:
                await self._client.set(full_key, serialized)

            logger.debug(f"Redis SET {full_key} (ttl={ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Redis SET error for {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis (auto JSON deserialize).

        Returns None if key doesn't exist.
        """
        try:
            full_key = self._make_key(key)
            data = await self._client.get(full_key)

            if data is None:
                return None

            logger.debug(f"Redis HIT {full_key}")
            return json.loads(data)

        except Exception as e:
            logger.error(f"Redis GET error for {key}: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        try:
            full_key = self._make_key(key)
            await self._client.delete(full_key)
            logger.debug(f"Redis DEL {full_key}")
            return True
        except Exception as e:
            logger.error(f"Redis DEL error for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            full_key = self._make_key(key)
            return bool(await self._client.exists(full_key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key"""
        try:
            full_key = self._make_key(key)
            return bool(await self._client.expire(full_key, ttl))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for {key}: {e}")
            return False

    # ─────────────────────────────────────────
    # HEALTH CHECK
    # ─────────────────────────────────────────

    async def health_check(self) -> bool:
        """Returns True if Redis is healthy"""
        try:
            return await self._client.ping()
        except Exception:
            return False

    async def get_info(self) -> dict:
        """Get Redis server info"""
        try:
            info = await self._client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────────

_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get or create singleton Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client
