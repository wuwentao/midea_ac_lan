"""Tests for Midea light entities."""

from unittest.mock import Mock, PropertyMock, call, patch

import pytest
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_EFFECT,
    ColorMode,
    LightEntityFeature,
)
from homeassistant.const import Platform
from midealan.devices.x13 import DeviceAttributes as X13Attributes

from custom_components.midea_ac_lan.light import MideaLight, async_setup_entry

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Create default and explicitly selected light controls."""
    install_config(
        {
            "default": {"type": Platform.LIGHT, "default": True},
            "selected": {"type": Platform.LIGHT},
            "ignored": {"type": Platform.LIGHT},
            "wrong": {"type": Platform.SENSOR, "default": True},
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    assert [item._entity_key for item in add_entities.call_args.args[0]] == [
        "default",
        "selected",
    ]


def make_light(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    values: dict[object, object],
) -> tuple[MideaLight, Mock, dict[object, object]]:
    """Create one registry-backed light with mutable device state."""
    install_config({"main": {"type": Platform.LIGHT}})
    device, state = device_factory(attributes=values)
    device.color_temp_range = (2700, 6500)
    device.effects = ["rainbow", "pulse"]
    return MideaLight(device, "main"), device, state


def test_supported_features_and_color_modes(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Recompute effects and the strongest available color capability."""
    light, _, values = make_light(device_factory, install_config, {})
    assert light.supported_features == LightEntityFeature(0)
    assert light.supported_color_modes == {ColorMode.ONOFF}
    assert light.color_mode is ColorMode.ONOFF

    values[X13Attributes.brightness] = 100
    assert light.supported_color_modes == {ColorMode.BRIGHTNESS}
    assert light.color_mode is ColorMode.BRIGHTNESS

    values[X13Attributes.color_temperature] = 3000
    assert light.supported_color_modes == {ColorMode.COLOR_TEMP}
    assert light.color_mode is ColorMode.COLOR_TEMP

    values[X13Attributes.rgb_color] = (255, 0, 0)
    assert light.supported_color_modes == {ColorMode.COLOR_TEMP, ColorMode.HS}
    assert light.color_mode is ColorMode.COLOR_TEMP
    with patch.object(
        MideaLight,
        "hs_color",
        new_callable=PropertyMock,
        return_value=(0, 100),
    ):
        assert light.color_mode is ColorMode.HS

    values[X13Attributes.effect] = "rainbow"
    assert light.supported_features is LightEntityFeature.EFFECT
    assert light._calc_color_mode(set()) is ColorMode.UNKNOWN


def test_light_properties(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose power, brightness, color, temperature, and effect state."""
    light, _, values = make_light(
        device_factory,
        install_config,
        {
            X13Attributes.power: True,
            X13Attributes.brightness: 128,
            X13Attributes.rgb_color: (1, 2, 3),
            X13Attributes.color_temperature: 4000,
            X13Attributes.effect: "pulse",
        },
    )
    assert light.is_on
    assert light.brightness == 128
    assert light.rgb_color == (1, 2, 3)
    assert light.color_temp_kelvin == 4000
    assert light.color_temp == 250
    assert light.min_color_temp_kelvin == 2700
    assert light.max_color_temp_kelvin == 6500
    assert light.effect_list == ["rainbow", "pulse"]
    assert light.effect == "pulse"
    values[X13Attributes.color_temperature] = None
    assert light.color_temp is None


def test_light_commands(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Power on as needed and forward supported command attributes."""
    light, device, values = make_light(
        device_factory,
        install_config,
        {X13Attributes.power: False},
    )
    light.turn_on(
        **{
            ATTR_BRIGHTNESS: 200,
            ATTR_COLOR_TEMP_KELVIN: 3500,
            ATTR_EFFECT: "pulse",
            "ignored": True,
        },
    )
    assert device.set_attribute.call_args_list == [
        call(attr=X13Attributes.power, value=True),
        call(attr=X13Attributes.brightness, value=200),
        call(attr=X13Attributes.color_temperature, value=3500),
        call(attr=X13Attributes.effect, value="pulse"),
    ]
    device.set_attribute.reset_mock()
    values[X13Attributes.power] = True
    light.turn_on()
    device.set_attribute.assert_not_called()
    for key, attribute, value in (
        (ATTR_BRIGHTNESS, X13Attributes.brightness, 200),
        (ATTR_COLOR_TEMP_KELVIN, X13Attributes.color_temperature, 3500),
        (ATTR_EFFECT, X13Attributes.effect, "pulse"),
    ):
        light.turn_on(**{key: value})
        device.set_attribute.assert_called_once_with(attr=attribute, value=value)
        device.set_attribute.reset_mock()
    light.turn_off(ignored=True)
    device.set_attribute.assert_called_once_with(attr=X13Attributes.power, value=False)


def test_update_state_attached_and_detached(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Refresh attached lights and safely ignore reports before HA attachment."""
    detached, _, _ = make_light(device_factory, install_config, {})
    detached.schedule_update_if_running = Mock()
    detached.update_state({})
    detached.schedule_update_if_running.assert_not_called()
    assert "Light update_state skipped for None" in caplog.text
    assert "MideaLight" in caplog.text

    attached, _, _ = make_light(device_factory, install_config, {})
    attached.hass = Mock()
    attached.schedule_update_if_running = Mock()
    attached.update_state({})
    attached.schedule_update_if_running.assert_called_once_with()
