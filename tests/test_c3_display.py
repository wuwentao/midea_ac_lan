"""C3 display values and model-scoped controls for native model 17100007."""

from typing import Any, cast
from unittest.mock import Mock

import pytest
from homeassistant.const import PRECISION_TENTHS, PRECISION_WHOLE
from midea_ac_lan.climate import MideaC3Climate
from midea_ac_lan.const import supports_device
from midea_ac_lan.midea_devices import MIDEA_DEVICES
from midea_ac_lan.water_heater import MideaC3WaterHeater
from midealan.devices.c3 import DeviceAttributes as C3Attributes

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


@pytest.mark.parametrize(
    ("zone", "attributes", "expected"),
    [
        (0, {"temp_t1": 26.1, "temp_ta": 21.5}, 26.1),
        (0, {"zone1_room_temp_mode": True, "temp_t1": 26.1, "temp_ta": 21.5}, 21.5),
        (1, {"temp_tw2": 31.4, "temp_t1": 26.1}, 31.4),
        (1, {"zone2_room_temp_mode": True, "temp_ta": 22.0}, 22.0),
        (0, {}, None),
        (1, {"temp_t1": 26.1}, None),
    ],
)
def test_c3_climate_current_temperature(
    zone: int,
    attributes: dict[str, Any],
    expected: float | None,
) -> None:
    """Water zones report leaving water, room zones report the room sensor."""
    climate = MideaC3Climate(
        controller(attributes),
        f"climate_zone{zone + 1}",
        zone,
    )
    assert climate.current_temperature == expected


def test_c3_water_heater_keeps_tank_tenths() -> None:
    """Tank T5 is reported in 0.1 °C; targets stay in whole degrees."""
    heater = MideaC3WaterHeater(
        controller({"tank_actual_temperature": 50.5}),
        "water_heater",
    )
    assert heater.precision == PRECISION_TENTHS
    assert heater.target_temperature_step == PRECISION_WHOLE
    assert heater.current_temperature == pytest.approx(50.5)


def test_c3_holiday_switch_hidden_for_native_model() -> None:
    """17100007 only reports holiday state, so no writable switch is offered."""
    entities = cast("dict[str, dict[str, Any]]", MIDEA_DEVICES[C3]["entities"])
    config = entities[C3Attributes.holiday_on]
    assert not supports_device("17100007", 0, config)
    assert supports_device("17100003", 0, config)


def test_excluded_models_does_not_affect_other_entities() -> None:
    """An empty exclusion list keeps the default model behaviour."""
    assert supports_device("17100007", 0, {"excluded_models": []})
    assert not supports_device("A", 0, {"models": ["B"], "excluded_models": []})
