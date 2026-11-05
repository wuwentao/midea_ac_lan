"""Tests for Midea select entities."""

from unittest.mock import Mock

import pytest
from homeassistant.const import Platform

from custom_components.midea_ac_lan.select import MideaSelect, async_setup_entry

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry_filters_entities(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add supported and enabled selects with available capabilities."""
    install_config(
        {
            "default": {"type": Platform.SELECT, "default": True, "options": []},
            "selected": {"type": Platform.SELECT, "options": []},
            "missing": {
                "type": Platform.SELECT,
                "default": True,
                "options": [],
                "required_attribute": "capability",
            },
            "unsupported": {
                "type": Platform.SELECT,
                "default": True,
                "options": [],
                "models": ["OTHER"],
            },
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


@pytest.mark.parametrize(
    ("config", "device_properties", "expected"),
    [
        ({"options": {1: "one", 2: "two"}}, {}, ["one", "two"]),
        ({"options": [1, "two"]}, {}, ["1", "two"]),
        ({"options": "modes"}, {"modes": ["auto", "sleep"]}, ["auto", "sleep"]),
        (
            {"options_dict": "mode_map", "options_exclude_codes": [2]},
            {"mode_map": {1: "one", 2: "two"}},
            ["one"],
        ),
        (
            {
                "options_dict": "mode_map",
                "options_codes": [2, 3, 9],
                "options_exclude_codes": [3],
            },
            {"mode_map": {1: "one", 2: "two", 3: "three"}},
            ["two"],
        ),
        (
            {
                "options_dict": "mode_map",
                "options_codes": [1],
                "options_codes_by_model": {"TEST-MODEL": [2]},
            },
            {"mode_map": {1: "one", 2: "two"}},
            ["two"],
        ),
    ],
)
def test_options_sources(
    config: dict[str, object],
    device_properties: dict[str, object],
    expected: list[str],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Build options from literals and public device metadata."""
    install_config({"mode": {"type": Platform.SELECT, **config}})
    device, _ = device_factory()
    for key, value in device_properties.items():
        setattr(device, key, value)
    assert MideaSelect(device, "mode").options == expected


def test_options_method_and_current_option(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use dynamic options and map reported state values."""
    install_config(
        {
            "mode": {
                "type": Platform.SELECT,
                "attribute": "write_mode",
                "state_attribute": "read_mode",
                "options_method": "get_parameter_options",
                "state_map": {1: "eco"},
            },
        },
    )
    device, values = device_factory(attributes={"read_mode": None})
    device.get_parameter_options.return_value = ["eco", "boost"]
    entity = MideaSelect(device, "mode")

    assert entity.options == ["eco", "boost"]
    device.get_parameter_options.assert_called_with("write_mode")
    assert entity.current_option is None
    values["read_mode"] = 1
    assert entity.current_option == "eco"
    values["read_mode"] = "missing"
    assert entity.current_option is None


def test_current_option_for_dict_and_list(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Translate dictionary codes and validate list-backed reports."""
    install_config({"mode": {"type": Platform.SELECT, "options": {1: "one"}}})
    device, values = device_factory(attributes={"mode": 1})
    assert MideaSelect(device, "mode").current_option == "one"
    values["mode"] = 2
    assert MideaSelect(device, "mode").current_option is None

    install_config({"mode": {"type": Platform.SELECT, "options": [1, 2]}})
    values["mode"] = 1
    assert MideaSelect(device, "mode").current_option == "1"
    values["mode"] = 3
    assert MideaSelect(device, "mode").current_option is None


def test_availability_and_selection(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Gate selects on power and convert outgoing option values."""
    install_config(
        {
            "mode": {
                "type": Platform.SELECT,
                "options": {1: "one", 2: "two"},
                "available_power_attribute": "power",
            },
        },
    )
    device, values = device_factory(attributes={"power": False})
    entity = MideaSelect(device, "mode")
    assert not entity.available
    values["power"] = True
    assert entity.available
    entity.select_option("two")
    device.set_attribute.assert_called_once_with("mode", 2)
    with pytest.raises(ValueError, match="Unsupported select option"):
        entity.select_option("missing")

    device.available = False
    assert not entity.available


def test_integer_and_dishwasher_selection(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Convert integer options and use the dishwasher public setter."""
    install_config(
        {
            "level": {
                "type": Platform.SELECT,
                "options": [1, 2],
                "option_type": "int",
            },
        },
    )
    device, _ = device_factory()
    MideaSelect(device, "level").select_option("2")
    device.set_attribute.assert_called_with("level", 2)

    install_config(
        {
            "mode": {
                "type": Platform.SELECT,
                "options_dict": "mode_map",
                "set_message": "e1_work_mode",
            },
        },
    )
    device.mode_map = {1: "eco"}
    entity = MideaSelect(device, "mode")
    entity.select_option("eco")
    device.set_work_mode.assert_called_once_with(1)
    with pytest.raises(ValueError, match="Unsupported dishwasher mode"):
        entity.select_option("missing")


def test_update_state_and_lookup(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Refresh power-sensitive selects and reverse-map option labels."""
    install_config(
        {
            "mode": {
                "type": Platform.SELECT,
                "options": ["a"],
                "available_power_attribute": "power",
            },
        },
    )
    device, _ = device_factory()
    entity = MideaSelect(device, "mode")
    entity.hass = Mock()
    entity.schedule_update_if_running = Mock()
    entity.update_state({"power": True})
    assert entity.schedule_update_if_running.call_count == 1
    entity.update_state({"mode": "a"})
    assert entity.schedule_update_if_running.call_count == 3
    entity.update_state({"unrelated": True})
    assert entity.schedule_update_if_running.call_count == 3
    assert MideaSelect._get_dict_key_by_value({1: "a"}, "a") == 1
    assert MideaSelect._get_dict_key_by_value({1: "a"}, "b") is None
