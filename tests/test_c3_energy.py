"""Native HA metadata, registration guards and bounded C3 control state."""

import asyncio
import json
from typing import Any, cast
from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS, Platform
from homeassistant.helpers.entity import EntityCategory
from midea_ac_lan.climate import MideaC3Climate
from midea_ac_lan.const import DEVICES, DOMAIN, supports_device
from midea_ac_lan.midea_devices import MIDEA_DEVICES
from midea_ac_lan.sensor import MideaSensor, async_setup_entry
from midea_ac_lan.water_heater import MideaC3WaterHeater

C3 = 0xC3
ENERGY_SENSOR_COUNT = 57
RECORDER_ATTRIBUTE_LIMIT = 16384
TEST_POWER = 1234.56
ENERGY_CONFIGS = {
    str(key): config
    for key, config in cast(
        "dict[str, dict[str, Any]]",
        MIDEA_DEVICES[C3]["entities"],
    ).items()
    if config.get("translation_key", "").startswith("c3_")
}


def controller(attributes: dict[str, Any]) -> Mock:
    """Build a controller without credentials, network access or HA setup."""
    device = Mock()
    device.device_type = C3
    device.device_id = 1
    device.name = "Offline C3"
    device.model = "17100007"
    device.subtype = 195
    device.available = True
    device.temperature_step = 0.5
    device.attributes = attributes
    device.get_attribute.side_effect = lambda attr: attributes.get(str(attr))
    return device


@pytest.mark.parametrize("key", sorted(ENERGY_CONFIGS))
def test_native_sensor_metadata_and_value(key: str) -> None:
    """Check actual entity properties, not JSON strings that bypass HA validation."""
    config = ENERGY_CONFIGS[key]
    device = controller({key: 2.5})
    sensor = MideaSensor(device, key)
    assert sensor.native_value == pytest.approx(2.5)
    assert isinstance(config["type"], Platform)
    assert sensor.entity_category is None or isinstance(
        sensor.entity_category,
        EntityCategory,
    )
    assert isinstance(sensor.state_class, SensorStateClass)
    assert sensor.device_class is None or isinstance(
        sensor.device_class,
        SensorDeviceClass,
    )
    assert config["required_attribute"] == key
    assert supports_device("17100007", 195, config)
    assert not supports_device("17100003", 195, config)
    assert not config.get("default")
    if sensor.device_class == SensorDeviceClass.POWER:
        assert sensor.native_unit_of_measurement == "kW"
    elif sensor.device_class == SensorDeviceClass.ENERGY:
        assert sensor.native_unit_of_measurement == "kWh"
    else:
        assert sensor.native_unit_of_measurement is None


def test_optional_entities_require_matching_library_attributes() -> None:
    """The unchanged dependency pin remains importable before library release."""
    assert len(ENERGY_CONFIGS) == ENERGY_SENSOR_COUNT
    device = controller({})
    hass = Mock()
    hass.data = {DOMAIN: {DEVICES: {1: device}}}
    entry = Mock()
    entry.data = {CONF_DEVICE_ID: 1}
    entry.options = {CONF_SENSORS: ["heating_power", "dhw_power_consumption"]}
    add = Mock()
    asyncio.run(async_setup_entry(hass, entry, add))
    add.assert_called_once_with([])
    device.attributes.update(heating_power=1.5, dhw_power_consumption=0.0)
    asyncio.run(async_setup_entry(hass, entry, add))
    entities = add.call_args.args[0]
    assert len(entities) == len(entry.options[CONF_SENSORS])
    assert [entity.native_value for entity in entities] == [1.5, 0.0]


def test_curated_telemetry_fits_both_control_entities() -> None:
    """Prevent the generated-attribute expansion from exceeding recorder's limit."""
    attributes: dict[str, Any] = dict.fromkeys(ENERGY_CONFIGS, TEST_POWER)
    attributes.update(zone1_power=True, dhw_power=False, zone_target_temp=[33.0, 25.0])
    device = controller(attributes)
    for entity in (
        MideaC3Climate(device, "climate_zone1", 0),
        MideaC3WaterHeater(device, "water_heater"),
    ):
        attrs = entity.extra_state_attributes
        assert len(json.dumps(attrs).encode()) < RECORDER_ATTRIBUTE_LIMIT
        assert attrs["heating_power"] == pytest.approx(TEST_POWER)
        assert not any(key.startswith("c3_") for key in attrs)
