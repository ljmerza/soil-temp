"""DataUpdateCoordinator for the Soil Temp (ClearAPI) integration."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ClearApiAuthError,
    ClearApiClient,
    ClearApiConnectionError,
    ClearApiError,
    ClearApiRateLimitError,
)
from .const import (
    API_FIELD_KEYS,
    AVG_5D_WINDOW,
    AVG_24H_WINDOW,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    LOOKBACK_DAYS,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class SoilSnapshot:
    """One coordinator update worth of soil data."""

    observation_date: str
    fetched_at: datetime
    location: tuple[float, float]
    values: dict[str, float | None] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    averages_24h: dict[str, float | None] = field(default_factory=dict)
    averages_5d: dict[str, float | None] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


class SoilTempCoordinator(DataUpdateCoordinator[SoilSnapshot]):
    """Polls ClearAPI's daily/soil endpoint for HA's home coordinates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ClearApiClient,
    ) -> None:
        scan_hours = int(
            entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS)
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(hours=scan_hours),
        )
        self._client = client
        self._entry = entry

    async def _async_update_data(self) -> SoilSnapshot:
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude
        if lat is None or lon is None:
            raise UpdateFailed("Home Assistant home coordinates are not set")

        now = int(time.time())
        start = now - LOOKBACK_DAYS * 86400

        try:
            payload = await self._client.fetch_daily_soil(lat, lon, start, now)
        except ClearApiAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except ClearApiRateLimitError as err:
            raise UpdateFailed(f"ClearAPI rate limited: {err}") from err
        except ClearApiConnectionError as err:
            raise UpdateFailed(f"Network error talking to ClearAPI: {err}") from err
        except ClearApiError as err:
            raise UpdateFailed(f"ClearAPI error: {err}") from err

        location_block = _extract_location_block(payload)
        if not location_block:
            raise UpdateFailed("ClearAPI response did not contain a location block")

        sorted_dates = sorted(
            d for d, day in location_block.items() if isinstance(day, dict) and day
        )
        if not sorted_dates:
            raise UpdateFailed("ClearAPI response had no daily observations")

        observation_date = sorted_dates[-1]
        last_24h_dates = sorted_dates[-AVG_24H_WINDOW:]
        last_5d_dates = sorted_dates[-AVG_5D_WINDOW:]

        values: dict[str, float | None] = {}
        units: dict[str, str] = {}
        averages_24h: dict[str, float | None] = {}
        averages_5d: dict[str, float | None] = {}

        latest_day = location_block.get(observation_date) or {}

        for key in API_FIELD_KEYS:
            entry_data = latest_day.get(key) if isinstance(latest_day, dict) else None
            if isinstance(entry_data, dict):
                values[key] = _coerce_float(entry_data.get("value"))
                unit = entry_data.get("unit")
                if isinstance(unit, str):
                    units[key] = unit
            else:
                values[key] = None

            averages_24h[key] = _mean_for_field(location_block, last_24h_dates, key)
            averages_5d[key] = _mean_for_field(location_block, last_5d_dates, key)

        snapshot = SoilSnapshot(
            observation_date=observation_date,
            fetched_at=datetime.now(timezone.utc),
            location=(lat, lon),
            values=values,
            units=units,
            averages_24h=averages_24h,
            averages_5d=averages_5d,
            raw=payload,
        )
        _LOGGER.debug(
            "Soil snapshot for %s,%s observation_date=%s days=%d fields=%d",
            lat,
            lon,
            observation_date,
            len(sorted_dates),
            sum(1 for v in values.values() if v is not None),
        )
        return snapshot


def _extract_location_block(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Return the per-date dict for the (single) location key in the response."""
    if not isinstance(payload, dict):
        return None
    for value in payload.values():
        if isinstance(value, dict):
            return value
    return None


def _mean_for_field(
    location_block: dict[str, Any],
    dates: list[str],
    key: str,
) -> float | None:
    """Mean of `key`'s value across the given dates (skipping missing entries)."""
    samples: list[float] = []
    for date_key in dates:
        day = location_block.get(date_key)
        if not isinstance(day, dict):
            continue
        entry_data = day.get(key)
        if not isinstance(entry_data, dict):
            continue
        value = _coerce_float(entry_data.get("value"))
        if value is not None:
            samples.append(value)
    if not samples:
        return None
    return sum(samples) / len(samples)


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
