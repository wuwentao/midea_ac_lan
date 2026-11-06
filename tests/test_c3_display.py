"""C3 display values and model-scoped controls for native model 17100007."""

from typing import Any, cast
from unittest.mock import Mock

import pytest
from homeassistant.const import PRECISION_TENTHS
from midealan.devices.c3 import DeviceAttributes as C3Attributes

from custom_components.midea_ac_lan.climate import MideaC3Climate
from custom_components.midea_ac_lan.const import supports_device
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.water_heater import MideaC3WaterHeater

C3 = 0xC3


def controller(attributes: dict[str, Any], model: str = "17100007") -> Mock:
    """Build an offline C3 controller mock."""
    device = Mock()
    device.device_type = C3
    device.device_id = 1
    device.name = "Offline C3"
    device.model = model
    device.subtype = 0
    device.available = True
    device.attributes = attributes
    device.get_attribute.side_effect = lambda attr: attributes.get(str(attr))
    return device


WATER = True
ROOM = False


@pytest.mark.parametrize("power", [True, False], ids=["on", "off"])
@pytest.mark.parametrize(
    ("zone", "temp_types", "expected"),
    [
        (0, [WATER, WATER], 40.0),
        (0, [ROOM, WATER], 21.5),
        (1, [WATER, WATER], 31.4),
        (1, [WATER, ROOM], 21.5),
        (0, [None, WATER], None),
        (1, [WATER, None], None),
    ],
)
def test_c3_climate_current_temperature(
    zone: int,
    temp_types: list[bool | None],
    expected: float | None,
    *,
    power: bool,
) -> None:
    """The sensor follows zone_temp_type, independent of zone power."""
    attributes: dict[str, Any] = {
        "zone_temp_type": temp_types,
        "zone1_power": power,
        "zone2_power": power,
        # Derived flags are False while a zone is off; they must not matter.
        "zone1_water_temp_mode": power and temp_types[0] is True,
        "zone1_room_temp_mode": power and temp_types[0] is False,
        "zone2_water_temp_mode": power and temp_types[1] is True,
        "zone2_room_temp_mode": power and temp_types[1] is False,
        "temp_t1": 40.0,
        "temp_tw2": 31.4,
        "temp_ta": 21.5,
    }
    climate = MideaC3Climate(controller(attributes), f"climate_zone{zone + 1}", zone)
    assert climate.native_current_temperature == expected


@pytest.mark.parametrize("temp_types", [None, [], [True]])
def test_c3_climate_current_temperature_without_type(
    temp_types: list[bool] | None,
) -> None:
    """A missing or short zone_temp_type list returns None."""
    climate = MideaC3Climate(
        controller({"zone_temp_type": temp_types, "temp_t1": 40.0, "temp_tw2": 31.4}),
        "climate_zone2",
        1,
    )
    assert climate.native_current_temperature is None


def test_c3_climate_current_temperature_missing_sensor() -> None:
    """A selected sensor the library has not decoded returns None."""
    climate = MideaC3Climate(
        controller({"zone_temp_type": [ROOM, WATER], "temp_t1": 40.0}),
        "climate_zone1",
        0,
    )
    assert climate.native_current_temperature is None


@pytest.mark.parametrize("step", [0.5, 1.0])
def test_c3_water_heater_keeps_tank_tenths(step: float) -> None:
    """Tank T5 shows tenths; the target step follows the device setting."""
    device = controller({"tank_actual_temperature": 50.5})
    device.temperature_step = step
    heater = MideaC3WaterHeater(device, "water_heater")
    assert heater.precision == PRECISION_TENTHS
    assert heater.target_temperature_step == step
    assert heater.native_current_temperature == pytest.approx(50.5)


def test_c3_water_heater_without_step() -> None:
    """No device step leaves the HA default in place."""
    device = controller({})
    device.temperature_step = None
    heater = MideaC3WaterHeater(device, "water_heater")
    assert heater.target_temperature_step is None


def test_c3_holiday_switch_hidden_for_native_model() -> None:
    """17100007 only reports holiday state, so no writable switch is offered."""
    entities = cast("dict[str, dict[str, Any]]", MIDEA_DEVICES[C3]["entities"])
    config = entities[C3Attributes.holiday_on]
    assert not supports_device("17100007", 0, config)
    assert supports_device("17100003", 0, config)


def test_c3_zone2_climate_follows_double_zone_capability() -> None:
    """Keep an opted-in Zone 2 climate unavailable on a single-zone unit."""
    attributes = {"double_zone": False, "zone_temp_type": [WATER, WATER]}
    climate = MideaC3Climate(controller(attributes), "climate_zone2", 1)
    assert not climate.available

    attributes["double_zone"] = True
    assert climate.available


def test_excluded_models_does_not_affect_other_entities() -> None:
    """An empty exclusion list keeps the default model behaviour."""
    assert supports_device("17100007", 0, {"excluded_models": []})
    assert not supports_device("A", 0, {"models": ["B"], "excluded_models": []})
