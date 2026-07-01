"""
Base HTTP Client for Hermes AI OS

Features:
- Automatic retry with exponential backoff
- Timeout handling
- Request/Response logging
- Error handling
"""

import asyncio
import time
from typing import Any, Dict, Optional
import httpx
from app.core.logger import get_logger

logger = get_logger(__name__)


class BaseClient:
    """
    Base async HTTP client with retry logic and logging.
    All LLM/external clients inherit from this.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # httpx async client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(self.timeout),
        )

    async def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        json: Optional[Dict] = None,
        **kwargs,
    ) -> httpx.Response:
        """
        Make HTTP request with automatic retry on failure.

        Retry strategy:
        - Attempt 1: immediate
        - Attempt 2: wait 1s
        - Attempt 3: wait 2s
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()

                logger.debug(
                    f"HTTP {method} {url} — attempt {attempt}/{self.max_retries}"
                )

                response = await self._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    **kwargs,
                )

                duration_ms = (time.time() - start_time) * 1000
                logger.debug(
                    f"HTTP {method} {url} — {response.status_code} in {duration_ms:.0f}ms"
                )

                response.raise_for_status()
                return response

            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt}/{self.max_retries}: {url}")

            except httpx.HTTPStatusError as e:
                # Don't retry 4xx client errors
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code}: {url}")
                    raise
                last_exception = e
                logger.warning(
                    f"Server error {e.response.status_code} on attempt {attempt}/{self.max_retries}"
                )

            except httpx.RequestError as e:
                last_exception = e
                logger.warning(f"Request error on attempt {attempt}/{self.max_retries}: {e}")

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries:
                wait_time = self.retry_delay * attempt  # 1s, 2s, 3s...
                logger.debug(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        # All retries exhausted
        logger.error(f"All {self.max_retries} attempts failed for {url}")
        raise last_exception

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET request with retry"""
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST request with retry"""
        return await self._request("POST", url, **kwargs)

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
