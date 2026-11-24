"""Tests for AC climate temperature-unit adaptation."""

from unittest.mock import Mock, call

import pytest
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from midealan.devices.ac import DeviceAttributes as ACAttributes

from tests.helpers import DeviceFactory, InstallConfig
from tests.test_climate import make_ac


def enable_fahrenheit_api(device: Mock) -> None:
    """Stub the library's public setpoint API for integration unit tests."""
    device.uses_fahrenheit_setpoint = True
    forward = {16.0: 60.0, 16.5: 61.0, 18.5: 65.0, 31.5: 89.0, 32.0: 89.6}
    reverse = {60.0: 16.0, 61.0: 16.5, 65.0: 18.5, 82.0: 28.0, 89.0: 31.5}
    device.target_temperature_for_display.side_effect = lambda value: (
        forward.get(value, value * 9 / 5 + 32)
        if device.uses_fahrenheit_setpoint
        else value
    )
    device.target_temperature_from_display.side_effect = lambda value: (
        reverse.get(value, (value - 32) * 5 / 9)
        if device.uses_fahrenheit_setpoint
        else value
    )


@pytest.mark.parametrize("model", ["00000Q11", "00000Q15", "20601026"])
def test_ac_lua_fahrenheit_lookup_api_controls_display(
    model: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use library conversion APIs regardless of model/subtype naming."""
    entity, device, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            ACAttributes.target_temperature: 16.5,
            ACAttributes.indoor_temperature: 19.0,
        },
        model=model,
        subtype=999,
    )
    enable_fahrenheit_api(device)

    assert entity.native_temperature_unit == UnitOfTemperature.FAHRENHEIT
    assert entity.native_target_temperature == 61
    assert entity.native_current_temperature == pytest.approx(66.2)
    assert entity.target_temperature_step == PRECISION_WHOLE
    device.target_temperature_for_display.assert_called_once_with(16.5)


def test_ac_lua_fahrenheit_lookup_commands_and_live_unit(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Delegate setpoint conversion and follow the library's live unit flag."""
    entity, device, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            ACAttributes.target_temperature: 18.5,
            ACAttributes.min_temperature: 16.0,
            ACAttributes.max_temperature: 31.5,
        },
        model="00000Q15",
    )
    enable_fahrenheit_api(device)

    assert entity.native_target_temperature == 65
    assert entity.min_temp == 60
    assert entity.max_temp == 89
    assert entity.native_target_temperature_low == 60
    assert entity.native_target_temperature_high == 89
    entity.set_temperature(**{ATTR_TEMPERATURE: 65})
    device.set_target_temperature.assert_called_once_with(
        target_temperature=18.5,
        mode=None,
        zone=None,
    )

    device.uses_fahrenheit_setpoint = False
    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_target_temperature == pytest.approx(18.5)
    assert entity.min_temp == pytest.approx(16.0)
    assert entity.max_temp == pytest.approx(31.5)
    assert entity.target_temperature_step == PRECISION_HALVES


def test_ac_model_24_without_library_support_keeps_celsius(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """The integration does not infer lookup support from model 24."""
    entity, device, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            ACAttributes.temp_fahrenheit: True,
            ACAttributes.target_temperature: 18.5,
            ACAttributes.indoor_temperature: 19.0,
        },
        model="24",
    )

    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_target_temperature == pytest.approx(18.5)
    assert entity.native_current_temperature == pytest.approx(19.0)
    assert entity.target_temperature_step == PRECISION_HALVES
    entity.set_temperature(**{ATTR_TEMPERATURE: 65})
    device.set_target_temperature.assert_called_once_with(
        target_temperature=65.0,
        mode=None,
        zone=None,
    )


def test_ac_lua_fahrenheit_lookup_fallbacks(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Keep physical readings arithmetic and use API fallback conversions."""
    entity, device, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            ACAttributes.target_temperature: 32.0,
            ACAttributes.indoor_temperature: None,
        },
        model="00000Q15",
    )
    enable_fahrenheit_api(device)

    assert entity.native_target_temperature == pytest.approx(89.6)
    assert entity.native_current_temperature is None
    entity.set_temperature(**{ATTR_TEMPERATURE: 100})
    assert device.set_target_temperature.call_args == call(
        target_temperature=38.0,
        mode=None,
        zone=None,
    )

    device.uses_fahrenheit_setpoint = False
    assert entity.native_target_temperature == pytest.approx(32.0)
    entity.set_temperature(**{ATTR_TEMPERATURE: 20})
    assert device.set_target_temperature.call_args_list[-1] == call(
        target_temperature=20.0,
        mode=None,
        zone=None,
    )
