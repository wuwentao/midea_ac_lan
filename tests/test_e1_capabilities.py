"""E1 selectors and usage sensors consume the library's model capabilities."""

from unittest.mock import Mock, patch

import pytest
from midea_ac_lan.select import MideaSelect
from midea_ac_lan.sensor import MideaEstimatedUsageSensor
from midealan.const import ProtocolVersion
from midealan.devices.e1 import DeviceAttributes, MideaE1Device


def _device(model: str) -> MideaE1Device:
    """Create an offline dishwasher using the real library mapping."""
    return MideaE1Device(
        name="Dishwasher",
        device_id=1,
        ip_address="127.0.0.1",
        port=6444,
        token="AA",  # ruff: ignore[hardcoded-password-func-arg]
        key="BB",
        device_protocol=ProtocolVersion.V3,
        model=model,
        subtype=1,
        customize="",
    )


@pytest.mark.parametrize(
    ("model", "options"),
    [("76000228", ["0", "2"]), ("760001EC", ["0", "1", "2", "3"])],
)
def test_load_options_from_library(model: str, options: list[str]) -> None:
    """Keep the existing model's Load control when adding a new model."""
    device = _device(model)
    selector = MideaSelect(device, DeviceAttributes.additional_setting)
    assert selector.options == options
    selector.select_option(options[-1])
    assert selector.current_option == options[-1]


@pytest.mark.parametrize("entity_key", [DeviceAttributes.program, "mode_select"])
def test_program_selection_uses_model_codes(entity_key: str) -> None:
    """Resolve self-clean to the European code rather than legacy 0x0A."""
    device = _device("760001EC")
    selector = MideaSelect(device, entity_key)
    assert selector.options == device.get_attribute_options(DeviceAttributes.program)
    assert "anion1" in selector.options
    with patch.object(device, "build_send") as send:
        selector.select_option("self_clean")
        if entity_key == DeviceAttributes.program:
            assert selector.current_option == "self_clean"
            device.set_attribute(DeviceAttributes.status, "work")
    assert send.call_args.args[0].mode == 0x10  # ruff: ignore[magic-value-comparison]


@pytest.mark.parametrize(
    ("key", "expected"),
    [("estimated_energy_consumption", 1.106), ("estimated_water_consumption", 9.7)],
)
def test_estimates_use_model_mode_and_count_once(key: str, expected: float) -> None:
    """Count completion using the same self-clean mapping as the selector."""
    device = _device("760001EC")
    sensor = MideaEstimatedUsageSensor(device, key)
    sensor.hass = Mock()
    sensor.platform = Mock()
    assert sensor.has_estimates
    assert "self_clean" in sensor.extra_state_attributes["known_modes"]
    device._attributes.update(status="running", progress="wash", mode="self_clean")
    sensor.update_state({"progress": "wash"})
    device._attributes.update(status="power_off", progress="complete", mode=None)
    sensor.update_state({"progress": "complete"})
    sensor.update_state({"progress": "complete"})
    assert sensor.native_value == expected


def test_unknown_model_has_no_estimates_or_load_options() -> None:
    """Unknown models do not offer fabricated Load options or estimates."""
    device = _device("unknown")
    assert not MideaSelect(device, DeviceAttributes.additional_setting).options
    assert not MideaEstimatedUsageSensor(
        device,
        "estimated_water_consumption",
    ).has_estimates
