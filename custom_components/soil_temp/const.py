"""Constants and sensor catalog for the Soil Temp (ClearAPI) integration."""
from __future__ import annotations

from dataclasses import dataclass

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
AVG_5D_WINDOW = 5
AVG_24H_WINDOW = 1

UNIT_INCHES = "in"

BUCKET_LATEST = "values"
BUCKET_AVG_24H = "averages_24h"
BUCKET_AVG_5D = "averages_5d"


@dataclass(frozen=True, kw_only=True)
class SoilSensorDescription(SensorEntityDescription):
    """SensorEntityDescription with hints for which coordinator bucket / API field to read."""

    source_field: str | None = None
    bucket: str = BUCKET_LATEST


def _temp(key: str, icon: str) -> SoilSensorDescription:
    return SoilSensorDescription(
        key=key,
        translation_key=key,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        icon=icon,
    )


def _moisture_inches(key: str, icon: str) -> SoilSensorDescription:
    return SoilSensorDescription(
        key=key,
        translation_key=key,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UNIT_INCHES,
        suggested_display_precision=2,
        icon=icon,
    )


def _diagnostic(key: str, icon: str) -> SoilSensorDescription:
    return SoilSensorDescription(
        key=key,
        translation_key=key,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=3,
        icon=icon,
    )


def _temp_avg(key: str, source_field: str, bucket: str, icon: str) -> SoilSensorDescription:
    return SoilSensorDescription(
        key=key,
        translation_key=key,
        source_field=source_field,
        bucket=bucket,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        suggested_display_precision=1,
        icon=icon,
    )


RAW_SENSOR_DESCRIPTIONS: tuple[SoilSensorDescription, ...] = (
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

COMPUTED_SENSOR_DESCRIPTIONS: tuple[SoilSensorDescription, ...] = (
    _temp_avg(
        "soil_temp_avg_24h_0to10cm",
        source_field="soil_temp_0to10cm",
        bucket=BUCKET_AVG_24H,
        icon="mdi:thermometer",
    ),
    _temp_avg(
        "soil_temp_avg_5d_0to10cm",
        source_field="soil_temp_0to10cm",
        bucket=BUCKET_AVG_5D,
        icon="mdi:thermometer",
    ),
)

SENSOR_DESCRIPTIONS: tuple[SoilSensorDescription, ...] = (
    RAW_SENSOR_DESCRIPTIONS + COMPUTED_SENSOR_DESCRIPTIONS
)

API_FIELD_KEYS: tuple[str, ...] = tuple(d.key for d in RAW_SENSOR_DESCRIPTIONS)
