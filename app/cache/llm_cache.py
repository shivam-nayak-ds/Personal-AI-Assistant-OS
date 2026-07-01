"""
LLM Cache for Hermes AI OS

Cache LLM responses in Redis to:
- Save money (same question → no API call)
- Reduce latency (2000ms → 5ms)
- Handle rate limits gracefully
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

from app.cache.redis_client import get_redis_client
from app.core.logger import get_logger

logger = get_logger(__name__)

# Cache TTLs
CACHE_TTL_SHORT = 60 * 60          # 1 hour  - for dynamic responses
CACHE_TTL_MEDIUM = 60 * 60 * 24    # 24 hours - for semi-static responses
CACHE_TTL_LONG = 60 * 60 * 24 * 7  # 7 days  - for static content


class LLMCache:
    """
    Cache for LLM API responses using Redis.

    Cache Key Strategy:
        md5(model + messages + temperature) → response

    This means:
    - Same question + same model = cache hit ✅
    - Different temperature = cache miss (intentional)
    - Different model = cache miss (intentional)
    """

    def __init__(self, default_ttl: int = CACHE_TTL_MEDIUM):
        self.default_ttl = default_ttl
        self.prefix = "llm_cache"

    def _make_cache_key(
        self,
        messages: List[Dict],
        model: str,
        temperature: float,
    ) -> str:
        """
        Create deterministic cache key from request parameters.
        MD5 hash of (model + messages + temperature)
        """
        key_data = json.dumps(
            {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            },
            sort_keys=True,
        )
        hash_str = hashlib.md5(key_data.encode()).hexdigest()
        return f"{self.prefix}:{hash_str}"

    async def get(
        self,
        messages: List[Dict],
        model: str,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """
        Get cached LLM response.

        Returns:
            str: Cached response text, or None if cache miss
        """
        try:
            redis = await get_redis_client()
            key = self._make_cache_key(messages, model, temperature)
            cached = await redis.get(key)

            if cached:
                logger.info(f"🎯 LLM Cache HIT — key: {key[:20]}...")
                return cached.get("response") if isinstance(cached, dict) else cached

            logger.debug(f"💨 LLM Cache MISS — key: {key[:20]}...")
            return None

        except Exception as e:
            logger.warning(f"LLM Cache GET error (skipping cache): {e}")
            return None

    async def set(
        self,
        messages: List[Dict],
        model: str,
        response: str,
        temperature: float = 0.7,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache an LLM response.

        Args:
            messages: Input messages
            model: LLM model used
            response: Response text to cache
            temperature: Temperature used (affects cache key)
            ttl: Custom TTL in seconds
        """
        try:
            redis = await get_redis_client()
            key = self._make_cache_key(messages, model, temperature)

            cache_data = {
                "response": response,
                "model": model,
                "message_count": len(messages),
            }

            success = await redis.set(key, cache_data, ttl=ttl or self.default_ttl)

            if success:
                logger.info(f"💾 LLM Cached — key: {key[:20]}... (ttl={ttl or self.default_ttl}s)")

            return success

        except Exception as e:
            logger.warning(f"LLM Cache SET error (skipping cache): {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching pattern"""
        try:
            redis = await get_redis_client()
            # Find all matching keys
            keys = await redis._client.keys(f"hermes:{self.prefix}:{pattern}*")
            if keys:
                await redis._client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching '{pattern}'")
            return len(keys)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis"""
        try:
            redis = await get_redis_client()
            info = await redis.get_info()
            return {
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "memory": info.get("used_memory_human", "N/A"),
            }
        except Exception as e:
            return {"error": str(e)}


# ─────────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────────

_llm_cache: Optional[LLMCache] = None


def get_llm_cache() -> LLMCache:
    """Get or create singleton LLM cache"""
    global _llm_cache
    if _llm_cache is None:
        _llm_cache = LLMCache()
    return _llm_cache
