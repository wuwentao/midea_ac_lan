"""Regression checks for the native temperature members on climate and water heaters.

Entities implement the ``native_*`` members. Home Assistant reads the public names
through the compatibility mixin on HA < 2026.11, so both paths must report the same
values.
"""

import pytest
from homeassistant.const import (
    MAJOR_VERSION,
    MINOR_VERSION,
    Platform,
    UnitOfTemperature,
)
from midealan.devices.ed import DeviceAttributes as EDAttributes
from midealan.devices.fb import DeviceAttributes as FBAttributes

from custom_components.midea_ac_lan.climate import (
    MideaEDTeaBarClimate,
    MideaFBClimate,
)
from custom_components.midea_ac_lan.water_heater import MideaE2WaterHeater

from .helpers import DeviceFactory, InstallConfig


def test_climate_temperature_members(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Report the live temperatures and the fixed setpoint range."""
    install_config({"fb": {"type": Platform.CLIMATE}})
    device, values = device_factory(
        attributes={FBAttributes.current_temperature: 22.5},
    )
    entity = MideaFBClimate(device, "fb")

    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_current_temperature == pytest.approx(22.5)
    assert entity.native_target_temperature_high == 35
    assert entity.native_target_temperature_low == 5
    values[FBAttributes.current_temperature] = 19.0
    assert entity.native_current_temperature == pytest.approx(19.0)


@pytest.mark.skipif(
    (MAJOR_VERSION, MINOR_VERSION) >= (2026, 11),
    reason="HA 2026.11+ reads native_* directly; the old names are deprecated there",
)
def test_climate_legacy_names_forward_to_native(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Forward the old names HA < 2026.11 reads to the native members."""
    install_config({"fb": {"type": Platform.CLIMATE}})
    device, _ = device_factory(attributes={FBAttributes.current_temperature: 22.5})
    entity = MideaFBClimate(device, "fb")

    assert entity.temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.current_temperature == pytest.approx(22.5)
    assert entity.target_temperature_high == 35
    assert entity.target_temperature_low == 5


def test_water_heater_temperature_members(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Report the live temperatures and the Celsius unit."""
    install_config({"e2": {"type": Platform.WATER_HEATER}})
    device, values = device_factory(
        attributes={"current_temperature": 41.0, "target_temperature": 55.0},
    )
    entity = MideaE2WaterHeater(device, "e2")

    assert entity.native_temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.native_current_temperature == pytest.approx(41.0)
    assert entity.native_target_temperature == pytest.approx(55.0)
    values["target_temperature"] = 60.0
    assert entity.native_target_temperature == pytest.approx(60.0)


@pytest.mark.skipif(
    (MAJOR_VERSION, MINOR_VERSION) >= (2026, 11),
    reason="HA 2026.11+ reads native_* directly; the old names are deprecated there",
)
def test_water_heater_legacy_names_forward_to_native(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Forward the old names HA < 2026.11 reads to the native members."""
    install_config({"e2": {"type": Platform.WATER_HEATER}})
    device, _ = device_factory(
        attributes={"current_temperature": 41.0, "target_temperature": 55.0},
    )
    entity = MideaE2WaterHeater(device, "e2")

    assert entity.temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.current_temperature == pytest.approx(41.0)
    assert entity.target_temperature == pytest.approx(55.0)


@pytest.mark.skipif(
    (MAJOR_VERSION, MINOR_VERSION) >= (2026, 11),
    reason="HA 2026.11+ reads native_* directly; the old names are deprecated there",
)
def test_tea_bar_legacy_names_forward_to_native(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Forward the tea bar's old names HA < 2026.11 reads to the native members."""
    install_config({"ed": {"type": Platform.CLIMATE}})
    device, _ = device_factory(
        attributes={
            EDAttributes.current_temperature: 60.0,
            EDAttributes.target_temperature: 85.0,
        },
    )
    entity = MideaEDTeaBarClimate(device, "ed")

    assert entity.temperature_unit == UnitOfTemperature.CELSIUS
    assert entity.current_temperature == pytest.approx(60.0)
    assert entity.target_temperature == pytest.approx(85.0)
