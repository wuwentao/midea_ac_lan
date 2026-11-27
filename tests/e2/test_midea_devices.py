"""Tests for E2 device entity configuration."""

from typing import cast

import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    Platform,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolume,
)
from homeassistant.helpers.entity import EntityCategory
from midealan.const import DeviceType
from midealan.devices.e2 import DeviceAttributes as E2Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES


def test_eplus_switch_config() -> None:
    """Expose E2 Capacity Plus as a switch with its own translation."""
    entities = cast(
        "dict[E2Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.E2]["entities"],
    )

    assert entities[E2Attributes.eplus] == {
        "type": Platform.SWITCH,
        "translation_key": "eplus",
        "name": "Capacity Plus",
        "icon": "mdi:water-plus",
    }


@pytest.mark.parametrize(
    ("attribute", "expected"),
    [
        (
            E2Attributes.half_heat,
            {
                "type": Platform.BINARY_SENSOR,
                "translation_key": "half_heat",
                "name": "Half Tank Heating",
                "icon": "mdi:circle-half-full",
            },
        ),
        (
            E2Attributes.bottom_heat,
            {
                "type": Platform.BINARY_SENSOR,
                "translation_key": "bottom_heat",
                "name": "Bottom Tank Heating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
        ),
        (
            E2Attributes.top_heat,
            {
                "type": Platform.BINARY_SENSOR,
                "translation_key": "top_heat",
                "name": "Top Tank Heating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
        ),
        (
            E2Attributes.fast_hot_power,
            {
                "type": Platform.BINARY_SENSOR,
                "translation_key": "fast_hot_power",
                "name": "Fast Heating",
                "icon": "mdi:water-boiler",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
        ),
        (
            E2Attributes.water_flow,
            {
                "type": Platform.BINARY_SENSOR,
                "translation_key": "water_flow",
                "name": "Water Flow",
                "icon": "mdi:water-pump",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
        ),
        (
            E2Attributes.heat_water_level,
            {
                "type": Platform.SENSOR,
                "translation_key": "heat_water_level",
                "name": "Heated Water Level",
                "icon": "mdi:water-percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        ),
        (
            E2Attributes.in_temperature,
            {
                "type": Platform.SENSOR,
                "translation_key": "in_temperature",
                "name": "Inlet Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        ),
        (
            E2Attributes.water_consumption,
            {
                "type": Platform.SENSOR,
                "translation_key": "water_consumption",
                "name": "Water Consumption",
                "icon": "mdi:water",
                "device_class": SensorDeviceClass.WATER,
                "unit": UnitOfVolume.LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
        ),
        (
            E2Attributes.day_water_consumption,
            {
                "type": Platform.SENSOR,
                "translation_key": "day_water_consumption",
                "name": "Daily Water Consumption",
                "icon": "mdi:water",
                "device_class": SensorDeviceClass.WATER,
                "unit": UnitOfVolume.LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
        ),
        (
            E2Attributes.volume,
            {
                "type": Platform.SENSOR,
                "translation_key": "volume",
                "name": "Tank Volume",
                "icon": "mdi:storage-tank",
                "unit": UnitOfVolume.LITERS,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        ),
        (
            E2Attributes.rate,
            {
                "type": Platform.SENSOR,
                "translation_key": "rate",
                "name": "Rated Power",
                "device_class": SensorDeviceClass.POWER,
                "unit": UnitOfPower.WATT,
                "entity_category": EntityCategory.DIAGNOSTIC,
            },
        ),
        (
            E2Attributes.efficient,
            {
                "type": Platform.SWITCH,
                "translation_key": "efficient",
                "name": "Smart Power Saving",
                "icon": "mdi:leaf",
            },
        ),
    ],
)
def test_extended_e2_entity_config(
    attribute: E2Attributes,
    expected: dict[str, object],
) -> None:
    """Expose verified E2 telemetry and Lua-backed controls as opt-in entities."""
    entities = cast(
        "dict[E2Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.E2]["entities"],
    )

    assert entities[attribute] == expected
