"""Tests for Midea switch entities."""

from unittest.mock import Mock, call

from homeassistant.const import Platform
from midealan.device import DeviceType
from midealan.devices.ed import DeviceAttributes as EDAttributes

from custom_components.midea_ac_lan.switch import (
    MideaEDTeaBarBoilSwitch,
    MideaEDTeaBarChildLockSwitch,
    MideaSwitch,
    async_setup_entry,
)

from .helpers import DeviceFactory, InstallConfig, setup_context


async def test_async_setup_entry_filters_entities(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add supported, selected switches with available capabilities."""
    install_config(
        {
            "default": {"type": Platform.SWITCH, "default": True},
            "selected": {"type": Platform.SWITCH},
            "missing": {
                "type": Platform.SWITCH,
                "default": True,
                "required_attribute": "capability",
            },
            "unsupported": {
                "type": Platform.SWITCH,
                "default": True,
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


async def test_async_setup_entry_uses_tea_bar_classes(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use the special ED command semantics for both tea-bar controls."""
    install_config(
        {
            "tea_bar": {"type": Platform.SWITCH, "default": True},
            "tea_bar_child_lock": {"type": Platform.SWITCH, "default": True},
            "ordinary": {"type": Platform.SWITCH, "default": True},
        },
        DeviceType.ED,
    )
    device, _ = device_factory(device_type=DeviceType.ED)
    hass, entry, add_entities = setup_context(device)
    await async_setup_entry(hass, entry, add_entities)
    assert [type(item) for item in add_entities.call_args.args[0]] == [
        MideaEDTeaBarBoilSwitch,
        MideaEDTeaBarChildLockSwitch,
        MideaSwitch,
    ]


def test_switch_state_and_commands(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Read mapped values and send configured on/off commands."""
    install_config(
        {
            "mode": {
                "type": Platform.SWITCH,
                "attribute": "write_mode",
                "state_attribute": "read_mode",
                "on_value": "enabled",
                "off_value": "disabled",
            },
        },
    )
    device, values = device_factory(attributes={"read_mode": "enabled"})
    entity = MideaSwitch(device, "mode")
    assert entity.is_on
    values["read_mode"] = "disabled"
    assert not entity.is_on
    assert not entity.assumed_state
    entity.turn_on()
    entity.turn_off()
    assert device.set_attribute.call_args_list == [
        call(attr="write_mode", value="enabled"),
        call(attr="write_mode", value="disabled"),
    ]


def test_optimistic_switch_state(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Publish the last optimistic command when no report exists."""
    install_config({"power": {"type": Platform.SWITCH, "optimistic": True}})
    device, values = device_factory(attributes={"power": None})
    entity = MideaSwitch(device, "power")
    entity.schedule_update_if_running = Mock()
    assert entity.is_on is None
    assert entity.assumed_state
    entity.turn_on()
    assert entity.is_on
    entity.schedule_update_if_running.assert_not_called()
    entity.hass = Mock()
    entity.turn_on()
    entity.turn_off()
    assert not entity.is_on
    assert entity.schedule_update_if_running.call_count == 2
    detached = MideaSwitch(device, "power")
    detached.turn_off()
    values["power"] = True
    assert entity.is_on


def test_tea_bar_switches(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map boil/dispense and child-lock attributes to switch semantics."""
    install_config(
        {
            "tea_bar": {"type": Platform.SWITCH},
            "tea_bar_child_lock": {"type": Platform.SWITCH},
        },
        DeviceType.ED,
    )
    device, values = device_factory(
        device_type=DeviceType.ED,
        attributes={
            EDAttributes.boiling: False,
            EDAttributes.dispensing: True,
            EDAttributes.child_lock: True,
        },
    )
    boil = MideaEDTeaBarBoilSwitch(device, "tea_bar")
    child_lock = MideaEDTeaBarChildLockSwitch(device, "tea_bar_child_lock")
    assert boil.is_on
    values[EDAttributes.dispensing] = False
    assert not boil.is_on
    assert child_lock.is_on
    boil.turn_on()
    boil.turn_off()
    child_lock.turn_on()
    child_lock.turn_off()
    assert device.set_attribute.call_args_list == [
        call(EDAttributes.boiling, True),
        call(EDAttributes.boiling, False),
        call(EDAttributes.child_lock, True),
        call(EDAttributes.child_lock, False),
    ]
