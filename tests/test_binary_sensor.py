"""Tests for Midea binary sensor entities."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform

from custom_components.midea_ac_lan.binary_sensor import (
    MideaBinarySensor,
    async_setup_entry,
)

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry_filters_entities(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add supported, selected sensors with available backing attributes."""
    entities = {
        "default": {"type": Platform.BINARY_SENSOR, "default": True},
        "selected": {"type": Platform.BINARY_SENSOR},
        "missing": {
            "type": Platform.BINARY_SENSOR,
            "default": True,
            "required_attribute": "capability",
        },
        "wrong_type": {"type": Platform.SENSOR, "default": True},
        "wrong_model": {
            "type": Platform.BINARY_SENSOR,
            "default": True,
            "models": ["OTHER"],
        },
    }
    install_config(entities)
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, sensors=["selected"])

    await async_setup_entry(hass, entry, add_entities)

    added = add_entities.call_args.args[0]
    assert [entity._entity_key for entity in added] == ["default", "selected"]


def test_binary_sensor_properties(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose the configured class and live boolean value."""
    install_config(
        {
            "door": {
                "type": Platform.BINARY_SENSOR,
                "device_class": BinarySensorDeviceClass.DOOR,
            },
        },
    )
    device, values = device_factory(attributes={"door": True})
    entity = MideaBinarySensor(device, "door")

    assert entity.device_class is BinarySensorDeviceClass.DOOR
    assert entity.is_on
    values["door"] = False
    assert not entity.is_on
