"""Tests for Midea number entities."""

from unittest.mock import Mock

from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import Platform

from custom_components.midea_ac_lan.number import MideaNumber, async_setup_entry

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry_filters_entities(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add supported, enabled numbers with their required attribute."""
    install_config(
        {
            "default": {"type": Platform.NUMBER, "default": True},
            "selected": {"type": Platform.NUMBER},
            "missing": {
                "type": Platform.NUMBER,
                "default": True,
                "required_attribute": "capability",
            },
            "wrong": {"type": Platform.SENSOR, "default": True},
            "unsupported": {
                "type": Platform.NUMBER,
                "default": True,
                "subtypes": [2],
            },
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, switches=["selected"])

    await async_setup_entry(hass, entry, add_entities)

    assert [item._entity_key for item in add_entities.call_args.args[0]] == [
        "default",
        "selected",
    ]


def test_number_bounds_metadata_and_value(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Resolve literal, device-attribute, and device-property bounds."""
    install_config(
        {
            "level": {
                "type": Platform.NUMBER,
                "min": "minimum",
                "max": 100,
                "step": "increment",
                "device_class": NumberDeviceClass.POWER,
                "unit": "W",
                "missing_values": [-1],
            },
        },
    )
    device, values = device_factory(
        attributes={"level": 25, "minimum": 0, "increment": None},
    )
    device.increment = 5
    entity = MideaNumber(device, "level")

    assert entity.native_min_value == 0
    assert entity.native_max_value == 100
    assert entity.native_step == 5
    assert entity._attr_device_class is NumberDeviceClass.POWER
    assert entity._attr_native_unit_of_measurement == "W"
    assert entity.native_value == 25
    values["level"] = -1
    assert entity.native_value is None
    assert not entity.assumed_state
    entity.set_native_value(50)
    device.set_attribute.assert_called_once_with("level", 50)


def test_optimistic_number_updates(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Return and publish the last command when the device has no report."""
    install_config(
        {
            "level": {
                "type": Platform.NUMBER,
                "min": 0,
                "max": 10,
                "step": 1,
                "attribute": "write_level",
                "optimistic": True,
            },
        },
    )
    device, _ = device_factory()
    entity = MideaNumber(device, "level")
    entity.schedule_update_if_running = Mock()

    assert entity.native_value is None
    assert entity.assumed_state
    entity.set_native_value(4)
    assert entity.native_value == 4
    entity.schedule_update_if_running.assert_not_called()

    entity.hass = Mock()
    entity.set_native_value(6)
    device.set_attribute.assert_called_with("write_level", 6)
    entity.schedule_update_if_running.assert_called_once_with()
