"""Config + Options flow for Soil Temp (ClearAPI)."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    MAX_SCAN_INTERVAL_HOURS,
    MIN_SCAN_INTERVAL_HOURS,
)

_LOGGER = logging.getLogger(__name__)


class SoilTempConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle initial setup."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude
        if lat is None or lon is None:
            return self.async_abort(reason="coordinates_not_set")

        await self.async_set_unique_id(f"{lat:.6f}_{lon:.6f}")
        self._abort_if_unique_id_configured()

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                description_placeholders={
                    "latitude": f"{lat:.4f}",
                    "longitude": f"{lon:.4f}",
                },
            )

        return self.async_create_entry(
            title=f"Soil Temp ({lat:.4f}, {lon:.4f})",
            data={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return SoilTempOptionsFlowHandler()


class SoilTempOptionsFlowHandler(OptionsFlow):
    """Handle option changes."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_HOURS
        )
        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL_HOURS, max=MAX_SCAN_INTERVAL_HOURS),
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
