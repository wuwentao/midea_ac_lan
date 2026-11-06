"""Tests for Midea water heater entities."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call

import pytest
from homeassistant.components.water_heater import WaterHeaterEntityFeature
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    STATE_OFF,
    STATE_ON,
    Platform,
    UnitOfTemperature,
)
from midealan.device import DeviceType
from midealan.devices.c3 import DeviceAttributes as C3Attributes
from midealan.devices.cd import DeviceAttributes as CDAttributes
from midealan.devices.e2 import DeviceAttributes as E2Attributes
from midealan.devices.e6 import DeviceAttributes as E6Attributes

from custom_components.midea_ac_lan.water_heater import (
    E2_TEMPERATURE_MAX,
    E2_TEMPERATURE_MIN,
    E3_TEMPERATURE_MAX,
    E3_TEMPERATURE_MIN,
    MideaC3WaterHeater,
    MideaCDWaterHeater,
    MideaE2WaterHeater,
    MideaE3WaterHeater,
    MideaE6WaterHeater,
    MideaWaterHeater,
    async_setup_entry,
)

from .helpers import DeviceFactory, InstallConfig, setup_context

ON_OFF_FEATURES = (
    WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF
)


@pytest.mark.parametrize(
    ("device_type", "expected_class"),
    [
        (DeviceType.E2, MideaE2WaterHeater),
        (DeviceType.E3, MideaE3WaterHeater),
        (DeviceType.E6, MideaE6WaterHeater),
        (DeviceType.C3, MideaC3WaterHeater),
        (DeviceType.CD, MideaCDWaterHeater),
    ],
)
async def test_async_setup_entry_device_classes(
    device_type: int,
    expected_class: type[MideaWaterHeater],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Select each supported water heater implementation."""
    config: dict[str, object] = {
        "type": Platform.WATER_HEATER,
        "default": True,
    }
    if device_type == DeviceType.E6:
        config["use"] = 0
    install_config(
        {
            "main": config,
            "selected": {
                "type": Platform.WATER_HEATER,
                **({"use": 1} if device_type == DeviceType.E6 else {}),
            },
            "ignored": {"type": Platform.WATER_HEATER},
            "unsupported": {
                "type": Platform.WATER_HEATER,
                "default": True,
                "models": ["OTHER"],
            },
            "wrong": {"type": Platform.SENSOR, "default": True},
        },
        device_type,
    )
    device, _ = device_factory(device_type=device_type)
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    entities = add_entities.call_args.args[0]
    assert [type(item) for item in entities] == [expected_class, expected_class]
    assert [item._entity_key for item in entities] == ["main", "selected"]


async def test_async_setup_entry_unknown_device(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Ignore water heater configs for unsupported device types."""
    install_config({"main": {"type": Platform.WATER_HEATER, "default": True}})
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device)
    await async_setup_entry(hass, entry, add_entities)
    add_entities.assert_called_once_with([])


def test_base_water_heater_properties_and_commands(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose generic metadata, state, and commands."""
    install_config({"main": {"type": Platform.WATER_HEATER}})
    attributes = {
        "power": True,
        "mode": "eco",
        "current_temperature": 42,
        "target_temperature": 50,
    }
    device, values = device_factory(attributes=attributes)
    device.temperature_step = 0.5
    device.preset_modes = ["eco", "boost"]
    heater = MideaWaterHeater(device, "main")
    assert heater.supported_features is WaterHeaterEntityFeature.TARGET_TEMPERATURE
    assert heater.extra_state_attributes == {
        **attributes,
        "target_temperature_step": 0.5,
    }
    assert heater.precision == pytest.approx(float(PRECISION_WHOLE))
    assert heater.temperature_unit is UnitOfTemperature.CELSIUS
    assert heater.current_operation == "eco"
    assert heater.current_temperature == 42
    assert heater.target_temperature == 50
    assert heater.operation_list == ["eco", "boost"]
    with pytest.raises(NotImplementedError):
        _ = heater.min_temp
    with pytest.raises(NotImplementedError):
        _ = heater.max_temp

    heater.set_temperature()
    heater.set_temperature(**{ATTR_TEMPERATURE: "55"})
    heater.set_operation_mode("boost")
    heater.turn_on()
    heater.turn_off()
    assert device.set_attribute.call_args_list == [
        call("target_temperature", 55.0),
        call(attr="mode", value="boost"),
        call(attr="power", value=True),
        call(attr="power", value=False),
    ]
    values["power"] = False
    assert heater.current_operation == STATE_OFF
    del device.preset_modes
    assert heater.operation_list is None
    plain_device, _ = device_factory(attributes={})
    del plain_device.temperature_step
    assert (
        "target_temperature_step"
        not in MideaWaterHeater(
            plain_device,
            "main",
        ).extra_state_attributes
    )


async def test_base_async_commands_and_updates(
    caplog: pytest.LogCaptureFixture,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Dispatch async power commands and guard detached update callbacks."""
    install_config({"main": {"type": Platform.WATER_HEATER}})
    device, _ = device_factory()
    heater = MideaWaterHeater(device, "main")
    executor = AsyncMock()
    heater.hass = SimpleNamespace(async_add_executor_job=executor)
    await heater.async_turn_on(source="test")
    await heater.async_turn_off(source="test")
    scheduled_on = executor.await_args_list[0].args[0]
    scheduled_off = executor.await_args_list[1].args[0]
    assert scheduled_on.func == heater.turn_on
    assert scheduled_on.keywords == {"source": "test"}
    assert scheduled_off.func == heater.turn_off
    assert scheduled_off.keywords == {"source": "test"}
    heater.schedule_update_if_running = Mock()
    heater.update_state({})
    heater.schedule_update_if_running.assert_called_once_with()

    detached = MideaWaterHeater(device, "main")
    detached.schedule_update_if_running = Mock()
    detached.update_state({})
    detached.schedule_update_if_running.assert_not_called()
    assert "Water update_state skipped for None" in caplog.text
    assert "MideaWaterHeater" in caplog.text


def test_e2_water_heater(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose E2 bounds, power state, and on/off support."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.E2)
    device, values = device_factory(
        device_type=DeviceType.E2,
        attributes={E2Attributes.power: True},
    )
    heater = MideaE2WaterHeater(device, "main")
    assert heater.current_operation == STATE_ON
    values[E2Attributes.power] = False
    assert heater.current_operation == STATE_OFF
    assert heater.min_temp == E2_TEMPERATURE_MIN
    assert heater.max_temp == E2_TEMPERATURE_MAX
    assert heater.supported_features == ON_OFF_FEATURES


@pytest.mark.parametrize(
    ("precision_halves", "expected"),
    [(False, PRECISION_WHOLE), (True, PRECISION_HALVES)],
)
def test_e3_water_heater(
    precision_halves: bool,
    expected: float,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose E3 bounds, precision, power state, and on/off support."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.E3)
    device, values = device_factory(
        device_type=DeviceType.E3,
        attributes={"power": True},
    )
    device.precision_halves = precision_halves
    heater = MideaE3WaterHeater(device, "main")
    assert heater.supported_features == ON_OFF_FEATURES
    assert heater.min_temp == E3_TEMPERATURE_MIN
    assert heater.max_temp == E3_TEMPERATURE_MAX
    assert heater.precision == pytest.approx(float(expected))
    assert heater.current_operation == STATE_ON
    values["power"] = False
    assert heater.current_operation == STATE_OFF


def test_c3_water_heater(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map all C3 domestic-hot-water attributes and commands."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.C3)
    device, values = device_factory(
        device_type=DeviceType.C3,
        attributes={
            C3Attributes.dhw_power: True,
            C3Attributes.tank_actual_temperature: 45,
            C3Attributes.dhw_target_temp: 50,
            C3Attributes.dhw_temp_min: 30,
            C3Attributes.dhw_temp_max: 60,
        },
    )
    heater = MideaC3WaterHeater(device, "main")
    assert heater.supported_features == ON_OFF_FEATURES
    assert heater.current_operation == STATE_ON
    assert heater.current_temperature == 45
    assert heater.target_temperature == 50
    assert heater.min_temp == 30
    assert heater.max_temp == 60
    heater.set_temperature()
    heater.set_temperature(**{ATTR_TEMPERATURE: 55})
    heater.turn_on()
    heater.turn_off()
    assert device.set_attribute.call_args_list == [
        call(C3Attributes.dhw_target_temp, 55.0),
        call(attr=C3Attributes.dhw_power, value=True),
        call(attr=C3Attributes.dhw_power, value=False),
    ]
    values[C3Attributes.dhw_power] = False
    assert heater.current_operation == STATE_OFF


@pytest.mark.parametrize("use", [0, 1])
def test_e6_water_heater(
    use: int,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map E6 heating and bathing channels to their indexed attributes."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.E6)
    attributes = {
        E6Attributes.main_power: True,
        E6Attributes.heating_power: True,
        E6Attributes.heating_leaving_temperature: 41,
        E6Attributes.bathing_leaving_temperature: 42,
        E6Attributes.heating_temperature: 51,
        E6Attributes.bathing_temperature: 52,
        E6Attributes.temperature_min: [30, 35],
        E6Attributes.temperature_max: [60, 65],
    }
    device, values = device_factory(device_type=DeviceType.E6, attributes=attributes)
    heater = MideaE6WaterHeater(device, "main", use)
    assert heater.supported_features == ON_OFF_FEATURES
    assert heater.current_operation == STATE_ON
    assert heater.current_temperature == 41 + use
    assert heater.target_temperature == 51 + use
    assert heater.min_temp == 30 + 5 * use
    assert heater.max_temp == 60 + 5 * use
    heater.set_temperature()
    heater.set_temperature(**{ATTR_TEMPERATURE: 55})
    heater.turn_on()
    heater.turn_off()
    assert device.set_attribute.call_args_list == [
        call(heater._target_temperature_attr, 55.0),
        call(attr=heater._power_attr, value=True),
        call(attr=heater._power_attr, value=False),
    ]
    if use == 0:
        values[E6Attributes.heating_power] = False
    else:
        values[E6Attributes.main_power] = False
    assert heater.current_operation == STATE_OFF


def test_e6_heating_requires_main_power(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Report heating off when the E6 main power is disabled."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.E6)
    device, _ = device_factory(
        device_type=DeviceType.E6,
        attributes={
            E6Attributes.main_power: False,
            E6Attributes.heating_power: True,
        },
    )
    assert MideaE6WaterHeater(device, "main", 0).current_operation == STATE_OFF


def test_cd_water_heater(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose CD temperature bounds and operation-mode support."""
    install_config({"main": {"type": Platform.WATER_HEATER}}, DeviceType.CD)
    device, _ = device_factory(
        device_type=DeviceType.CD,
        attributes={
            CDAttributes.min_temperature: 10,
            CDAttributes.max_temperature: 70,
        },
    )
    heater = MideaCDWaterHeater(device, "main")
    assert heater.supported_features == (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.ON_OFF
        | WaterHeaterEntityFeature.OPERATION_MODE
    )
    assert heater.min_temp == 10
    assert heater.max_temp == 70
