"""Constants and sensor catalog for the Soil Temp (ClearAPI) integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "soil_temp"

API_BASE = "https://ag.us.clearapis.com/v1.1/daily/soil"

DEFAULT_APP_ID = "a2f0d7a4"
DEFAULT_APP_KEY = "742a069efe55c7015c2245032fb16bbb"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL_HOURS = 6
MIN_SCAN_INTERVAL_HOURS = 1
MAX_SCAN_INTERVAL_HOURS = 24

LOOKBACK_DAYS = 7

UNIT_INCHES = "in"


def _temp(key: str, icon: str) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=key,
        translation_key=key,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        icon=icon,
    )


def _moisture_inches(key: str, icon: str) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=key,
        translation_key=key,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_INCHES,
        suggested_display_precision=2,
        icon=icon,
    )


def _diagnostic(key: str, icon: str) -> SensorEntityDescription:
    return SensorEntityDescription(
        key=key,
        translation_key=key,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=3,
        icon=icon,
    )


SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    _temp("soil_temp_0to10cm", "mdi:thermometer"),
    _temp("soil_temp_max_0to10cm", "mdi:thermometer-high"),
    _temp("soil_temp_min_0to10cm", "mdi:thermometer-low"),
    _diagnostic("normalized_soil_temp_0to10cm", "mdi:sigma"),
    _moisture_inches("soil_moisture_0to10cm", "mdi:water"),
    _diagnostic("scaled_soil_moisture_0to10cm", "mdi:water-percent"),
    _diagnostic("abs_scaled_soil_moisture_0to10cm", "mdi:water-percent"),
    _diagnostic("abs_scaled_paw_soil_moisture_0to10cm", "mdi:sprout"),
    _diagnostic("normalized_soil_moisture_0to10cm", "mdi:sigma"),
    _moisture_inches("soil_moisture_0to200cm", "mdi:water"),
    _diagnostic("scaled_soil_moisture_0to200cm", "mdi:water-percent"),
    _diagnostic("abs_scaled_soil_moisture_0to200cm", "mdi:water-percent"),
    _diagnostic("abs_scaled_paw_soil_moisture_0to200cm", "mdi:sprout"),
    _diagnostic("normalized_soil_moisture_0to200cm", "mdi:sigma"),
)

SENSOR_KEYS: tuple[str, ...] = tuple(d.key for d in SENSOR_DESCRIPTIONS)
