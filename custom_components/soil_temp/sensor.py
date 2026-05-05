"""Sensor entities for Soil Temp (ClearAPI)."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BUCKET_LATEST, DOMAIN, SENSOR_DESCRIPTIONS, SoilSensorDescription
from .coordinator import SoilTempCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SoilTempCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SoilTempSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class SoilTempSensor(CoordinatorEntity[SoilTempCoordinator], SensorEntity):
    """A single ClearAPI soil metric exposed as a HA sensor."""

    _attr_has_entity_name = True

    entity_description: SoilSensorDescription

    def __init__(
        self,
        coordinator: SoilTempCoordinator,
        entry: ConfigEntry,
        description: SoilSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Soil Temp",
            manufacturer="ClearAPI",
            model="Daily Soil",
            configuration_url="https://ag.us.clearapis.com",
        )

    @property
    def native_value(self) -> float | None:
        snapshot = self.coordinator.data
        if snapshot is None:
            return None
        bucket = getattr(snapshot, self.entity_description.bucket, None)
        if not isinstance(bucket, dict):
            return None
        source = self.entity_description.source_field or self.entity_description.key
        return bucket.get(source)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        snapshot = self.coordinator.data
        if snapshot is None:
            return {}
        lat, lon = snapshot.location
        source = self.entity_description.source_field or self.entity_description.key
        attrs: dict[str, Any] = {
            "observation_date": snapshot.observation_date,
            "fetched_at": snapshot.fetched_at.isoformat(),
            "location": f"{lat},{lon}",
        }
        if self.entity_description.bucket == BUCKET_LATEST:
            attrs["api_unit"] = snapshot.units.get(source)
        else:
            attrs["source_field"] = source
            attrs["window"] = self.entity_description.bucket.removeprefix("averages_")
        return attrs
