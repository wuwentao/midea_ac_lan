"""Tests for Midea humidifier entities."""

from unittest.mock import Mock, call

import pytest
from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntityFeature,
)
from homeassistant.const import Platform
from midealan.device import DeviceType

from custom_components.midea_ac_lan.humidifier import (
    MideaA1Humidifier,
    MideaFDHumidifier,
    MideaHumidifier,
    async_setup_entry,
)

from .helpers import DeviceFactory, InstallConfig, setup_context


@pytest.mark.parametrize(
    ("device_type", "expected_class"),
    [
        (DeviceType.A1, MideaA1Humidifier),
        (DeviceType.FD, MideaFDHumidifier),
    ],
)
async def test_async_setup_entry(
    device_type: int,
    expected_class: type[MideaHumidifier],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Create the device-specific class for default and selected controls."""
    install_config(
        {
            "default": {"type": Platform.HUMIDIFIER, "default": True},
            "selected": {"type": Platform.HUMIDIFIER},
            "ignored": {"type": Platform.HUMIDIFIER},
            "wrong": {"type": Platform.SENSOR, "default": True},
        },
        device_type,
    )
    device, _ = device_factory(device_type=device_type)
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    added = add_entities.call_args.args[0]
    assert [type(item) for item in added] == [expected_class, expected_class]
    assert [item._entity_key for item in added] == ["default", "selected"]


async def test_async_setup_entry_unknown_device_type(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Do not construct a generic humidifier for an unknown device type."""
    install_config({"main": {"type": Platform.HUMIDIFIER, "default": True}})
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device)
    await async_setup_entry(hass, entry, add_entities)
    add_entities.assert_called_once_with([])


@pytest.mark.parametrize(
    ("entity_class", "device_class"),
    [
        (MideaA1Humidifier, HumidifierDeviceClass.DEHUMIDIFIER),
        (MideaFDHumidifier, HumidifierDeviceClass.HUMIDIFIER),
    ],
)
def test_humidifier_properties_and_commands(
    entity_class: type[MideaHumidifier],
    device_class: HumidifierDeviceClass,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose humidity, mode, metadata, power, and setter commands."""
    device_type = DeviceType.A1 if entity_class is MideaA1Humidifier else DeviceType.FD
    install_config({"main": {"type": Platform.HUMIDIFIER}}, device_type)
    device, values = device_factory(
        device_type=device_type,
        attributes={
            "current_humidity": 45.5,
            "target_humidity": 55,
            "mode": "auto",
            "power": True,
        },
    )
    device.modes = ["auto", "sleep"]
    entity = entity_class(device, "main")

    assert entity.current_humidity == pytest.approx(45.5)
    assert entity.target_humidity == 55
    assert entity.mode == "auto"
    assert entity.available_modes == ["auto", "sleep"]
    assert entity.is_on
    assert entity._attr_min_humidity == 35
    assert entity._attr_max_humidity == 85
    assert entity._attr_device_class is device_class
    assert entity._attr_supported_features is HumidifierEntityFeature.MODES
    entity.set_humidity(60)
    entity.set_mode("sleep")
    entity.turn_on()
    entity.turn_off()
    assert device.set_attribute.call_args_list == [
        call("target_humidity", 60),
        call("mode", "sleep"),
        call(attr="power", value=True),
        call(attr="power", value=False),
    ]
    values["power"] = False
    assert not entity.is_on


def test_update_state_attached_and_detached(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Refresh attached entities and safely ignore pre-HA reports."""
    install_config({"main": {"type": Platform.HUMIDIFIER}}, DeviceType.A1)
    device, _ = device_factory(device_type=DeviceType.A1)
    detached = MideaA1Humidifier(device, "main")
    detached.schedule_update_if_running = Mock()
    detached.update_state({})
    detached.schedule_update_if_running.assert_not_called()
    assert "Humidifier update_state skipped for None" in caplog.text
    assert "MideaA1Humidifier" in caplog.text

    attached = MideaA1Humidifier(device, "main")
    attached.hass = Mock()
    attached.schedule_update_if_running = Mock()
    attached.update_state({})
    attached.schedule_update_if_running.assert_called_once_with()
