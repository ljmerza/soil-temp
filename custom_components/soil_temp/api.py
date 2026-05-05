"""ClearAPI HTTP client for the daily soil endpoint."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE

_LOGGER = logging.getLogger(__name__)


class ClearApiError(Exception):
    """Base error for ClearAPI failures."""


class ClearApiAuthError(ClearApiError):
    """ClearAPI rejected the credentials (HTTP 401/403)."""


class ClearApiRateLimitError(ClearApiError):
    """ClearAPI rate limited the request (HTTP 429)."""


class ClearApiConnectionError(ClearApiError):
    """Network failure reaching ClearAPI."""


class ClearApiClient:
    """Minimal async wrapper around ClearAPI's daily/soil endpoint."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        app_id: str,
        app_key: str,
    ) -> None:
        self._session = session
        self._app_id = app_id
        self._app_key = app_key

    async def fetch_daily_soil(
        self,
        lat: float,
        lon: float,
        start: int,
        end: int,
    ) -> dict[str, Any]:
        params = {
            "app_id": self._app_id,
            "app_key": self._app_key,
            "location": f"{lat},{lon}",
            "start": str(start),
            "end": str(end),
        }
        try:
            async with self._session.get(
                API_BASE,
                params=params,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status in (401, 403):
                    raise ClearApiAuthError(
                        f"ClearAPI rejected credentials (HTTP {resp.status})"
                    )
                if resp.status == 429:
                    raise ClearApiRateLimitError("ClearAPI rate limit exceeded")
                resp.raise_for_status()
                # ClearAPI returns valid JSON but advertises Content-Type: text/html.
                # Disable aiohttp's content-type check so the body still decodes.
                return await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise ClearApiConnectionError(str(err)) from err
