"""Tests for Midea fan entities."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call

import pytest
from homeassistant.const import Platform
from midealan.device import DeviceType
from midealan.devices.ac import DeviceAttributes as ACAttributes
from midealan.devices.ce import DeviceAttributes as CEAttributes
from midealan.devices.x40 import DeviceAttributes as X40Attributes

from custom_components.midea_ac_lan.fan import (
    BGF10000_SUBTYPE,
    MideaACFreshAirFan,
    MideaB6Fan,
    MideaCEFan,
    MideaFAFan,
    MideaFan,
    MideaX40Fan,
    async_setup_entry,
)
from custom_components.midea_ac_lan.midea_devices import (
    FRESH_AIR_EXHAUST,
    FRESH_AIR_EXHAUST_MODE,
    FRESH_AIR_EXHAUST_POWER,
    FRESH_AIR_EXHAUST_SPEED,
)

from .helpers import DeviceFactory, InstallConfig, setup_context


@pytest.mark.parametrize(
    ("device_type", "expected_class"),
    [
        (DeviceType.FA, MideaFAFan),
        (DeviceType.B6, MideaB6Fan),
        (DeviceType.AC, MideaACFreshAirFan),
        (DeviceType.CE, MideaCEFan),
        (DeviceType.X40, MideaX40Fan),
    ],
)
async def test_async_setup_entry_device_classes(
    device_type: int,
    expected_class: type[MideaFan],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Select each supported device-specific fan class."""
    install_config(
        {
            "main": {"type": Platform.FAN, "default": True},
            "selected": {"type": Platform.FAN},
            "ignored": {"type": Platform.FAN},
            "missing": {
                "type": Platform.FAN,
                "default": True,
                "required_attribute": "capability",
            },
            "wrong": {"type": Platform.SENSOR, "default": True},
        },
        device_type,
    )
    device, _ = device_factory(device_type=device_type)
    device.speed_count = 5
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    assert [type(item) for item in add_entities.call_args.args[0]] == [
        expected_class,
        expected_class,
    ]


async def test_async_setup_entry_unknown_device(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Ignore fan configs for device types without a fan implementation."""
    install_config({"main": {"type": Platform.FAN, "default": True}})
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device)
    await async_setup_entry(hass, entry, add_entities)
    add_entities.assert_called_once_with([])


def test_base_fan_properties_and_commands(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose generic state and forward common fan commands."""
    install_config({"main": {"type": Platform.FAN}})
    device, values = device_factory(
        attributes={
            "power": True,
            "oscillate": True,
            "mode": "eco",
            "fan_speed": 2,
        },
    )
    device.preset_modes = ["normal", "eco"]
    fan = MideaFan(device, "main")
    fan._attr_speed_count = 5
    assert fan.preset_modes == ["normal", "eco"]
    assert fan.is_on
    assert fan.oscillating
    assert fan.preset_mode == "eco"
    assert fan.fan_speed == 2
    assert fan.percentage == 40
    fan.turn_off()
    fan.oscillate(False)
    fan.set_preset_mode("ECO mode")
    fan.set_percentage(60)
    assert device.set_attribute.call_args_list == [
        call(attr="power", value=False),
        call(attr="oscillate", value=False),
        call(attr="mode", value="ECO mode"),
        call(attr="fan_speed", value=3),
    ]
    values["fan_speed"] = 0
    assert fan.percentage is None
    del device.preset_modes
    assert fan.preset_modes is None


async def test_base_async_percentage_and_updates(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Turn off at zero and dispatch non-zero speed work to the executor."""
    install_config({"main": {"type": Platform.FAN}})
    device, _ = device_factory()
    fan = MideaFan(device, "main")
    fan.async_turn_off = AsyncMock()
    executor = AsyncMock()
    fan.hass = SimpleNamespace(async_add_executor_job=executor)
    await fan.async_set_percentage(0)
    fan.async_turn_off.assert_awaited_once_with()
    await fan.async_set_percentage(50)
    executor.assert_awaited_once_with(fan.set_percentage, 50)

    fan.schedule_update_if_running = Mock()
    fan.update_state({})
    fan.schedule_update_if_running.assert_called_once_with()
    detached = MideaFan(device, "main")
    detached.schedule_update_if_running = Mock()
    detached.update_state({})
    detached.schedule_update_if_running.assert_not_called()


@pytest.mark.parametrize("fan_class", [MideaFAFan, MideaB6Fan])
def test_standard_device_fans(
    fan_class: type[MideaFAFan | MideaB6Fan],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Configure speed counts and translate percentages for FA/B6 fans."""
    device_type = DeviceType.FA if fan_class is MideaFAFan else DeviceType.B6
    install_config({"main": {"type": Platform.FAN}}, device_type)
    device, _ = device_factory(device_type=device_type)
    device.speed_count = 4
    fan = fan_class(device, "main")
    assert fan._attr_speed_count == 4
    fan.turn_on(percentage=75, preset_mode="sleep")
    device.turn_on.assert_called_once_with(fan_speed=3, mode="sleep")
    device.turn_on.reset_mock()
    fan.turn_on()
    device.turn_on.assert_called_once_with(fan_speed=None, mode=None)


def test_fa_model_translation(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use the verified BGF10000 display translation only for its subtype."""
    install_config({"main": {"type": Platform.FAN}}, DeviceType.FA)
    device, _ = device_factory(
        device_type=DeviceType.FA,
        model="BGF10000",
        subtype=BGF10000_SUBTYPE,
    )
    device.speed_count = 4
    assert MideaFAFan(device, "main")._attr_translation_key == "bgf10000"
    device.subtype = 1
    assert MideaFAFan(device, "main")._attr_translation_key is None


@pytest.mark.parametrize("entity_key", ["fresh_air", FRESH_AIR_EXHAUST])
def test_fresh_air_fan(
    entity_key: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map normal and exhaust fresh-air controls to their respective attributes."""
    install_config({entity_key: {"type": Platform.FAN}}, DeviceType.AC)
    is_exhaust = entity_key == FRESH_AIR_EXHAUST
    power = FRESH_AIR_EXHAUST_POWER if is_exhaust else ACAttributes.fresh_air_power
    speed = FRESH_AIR_EXHAUST_SPEED if is_exhaust else ACAttributes.fresh_air_fan_speed
    mode = FRESH_AIR_EXHAUST_MODE if is_exhaust else ACAttributes.fresh_air_mode
    device, _ = device_factory(
        device_type=DeviceType.AC,
        attributes={power: True, speed: 25, mode: "auto"},
    )
    device.fresh_air_fan_speeds = ["auto"]
    device.fresh_air_exhaust_fan_speeds = ["low", "high"]
    fan = MideaACFreshAirFan(device, entity_key)
    assert fan.preset_modes == (["low", "high"] if is_exhaust else ["auto"])
    assert fan.is_on
    assert fan.fan_speed == 25
    assert fan.preset_mode == "auto"
    fan.turn_on(preset_mode="high")
    fan.turn_on(percentage=50)
    fan.turn_on()
    fan.turn_off()
    assert device.set_attribute.call_args_list == [
        call(attr=mode, value="high"),
        call(attr=speed, value=50),
        call(attr=power, value=True),
        call(attr=power, value=False),
    ]


def test_fresh_air_exhaust_missing_presets(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Return an empty exhaust preset list on older library devices."""
    install_config({FRESH_AIR_EXHAUST: {"type": Platform.FAN}}, DeviceType.AC)
    device, _ = device_factory(device_type=DeviceType.AC)
    del device.fresh_air_exhaust_fan_speeds
    assert MideaACFreshAirFan(device, FRESH_AIR_EXHAUST).preset_modes == []


async def test_ce_fan(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use CE power commands and always dispatch percentage through executor."""
    install_config({"main": {"type": Platform.FAN}}, DeviceType.CE)
    device, _ = device_factory(device_type=DeviceType.CE)
    device.speed_count = 3
    fan = MideaCEFan(device, "main")
    fan.turn_on(percentage=50, preset_mode="eco")
    device.set_attribute.assert_called_once_with(attr=CEAttributes.power, value=True)
    executor = AsyncMock()
    fan.hass = SimpleNamespace(async_add_executor_job=executor)
    await fan.async_set_percentage(0)
    executor.assert_awaited_once_with(fan.set_percentage, 0)


def test_x40_fan(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map the two-speed X40 fan's power state to its raw speed attribute."""
    install_config({"main": {"type": Platform.FAN}}, DeviceType.X40)
    device, values = device_factory(
        device_type=DeviceType.X40,
        attributes={X40Attributes.fan_speed: 1},
    )
    fan = MideaX40Fan(device, "main")
    assert fan.is_on
    values[X40Attributes.fan_speed] = 0
    assert not fan.is_on
    fan.turn_on(percentage=50, preset_mode="ignored")
    fan.turn_off()
    assert device.set_attribute.call_args_list == [
        call(attr=X40Attributes.fan_speed, value=1),
        call(attr=X40Attributes.fan_speed, value=0),
    ]
