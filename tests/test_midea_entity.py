"""Regression checks for capability-driven availability in ``midea_entity``.

The shared ``MideaEntity`` base gates availability on ``available_attribute`` /
``available_value_attribute`` and refreshes on mapped report attributes. These
checks exercise every laundry control the washer (0xDB) and dryer (0xDC) register
with such a capability gate, plus the 0x9B oven door select whose report and
write attributes differ.
"""

from typing import TYPE_CHECKING, cast
from unittest.mock import Mock, patch

import pytest
from homeassistant.const import Platform
from midea_ac_lan.button import MideaButton
from midea_ac_lan.midea_devices import MIDEA_DEVICES
from midea_ac_lan.number import MideaNumber
from midea_ac_lan.select import MideaSelect
from midea_ac_lan.switch import MideaSwitch
from midea_ac_lan.time import MideaTime

if TYPE_CHECKING:
    from midea_ac_lan.midea_entity import MideaEntity

ENTITY_CLASSES = {
    Platform.BUTTON: MideaButton,
    Platform.NUMBER: MideaNumber,
    Platform.SELECT: MideaSelect,
    Platform.SWITCH: MideaSwitch,
    Platform.TIME: MideaTime,
}


def _gated_controls() -> list[tuple["MideaEntity", dict[str, bool], str]]:
    """Build every laundry control (0xDB and 0xDC) gated by an SDK capability."""
    controls: list[tuple[MideaEntity, dict[str, bool], str]] = []
    for device_type in (0xDB, 0xDC):
        configs = cast("dict", MIDEA_DEVICES[device_type]["entities"])
        for key, config in configs.items():
            capability = config.get("available_attribute")
            if not capability:
                continue
            attributes = {capability: True}
            if value_attribute := config.get("available_value_attribute"):
                attributes[value_attribute] = True
            device = Mock()
            device.device_type = device_type
            device.device_id = 1
            device.name = "Offline availability test"
            device.available = True
            device.get_attribute.side_effect = attributes.get
            entity = ENTITY_CLASSES[config["type"]](device, key)
            entity.hass = Mock()
            entity.platform = Mock()
            controls.append((entity, attributes, capability))
    return controls


GATED_CONTROLS = _gated_controls()


def _control_id(control: tuple["MideaEntity", dict[str, bool], str]) -> str:
    """Name the parametrized case after its entity id for readable output."""
    return str(control[0].entity_id)


def test_gated_controls_discovered() -> None:
    """Fail loudly if the capability-gated laundry controls disappear."""
    assert GATED_CONTROLS


@pytest.mark.parametrize("control", GATED_CONTROLS, ids=_control_id)
def test_capability_only_updates_publish_both_transitions(
    control: tuple["MideaEntity", dict[str, bool], str],
) -> None:
    """Publish availability even when the control's own value is unchanged."""
    entity, attributes, capability = control
    assert entity.available
    for available in (False, True):
        attributes[capability] = available
        with patch.object(entity, "schedule_update_if_running") as refresh:
            entity.update_state({capability: available})
        refresh.assert_called_once_with()
        assert entity.available == available


def test_mapped_report_updates_preserve_separate_write_attribute() -> None:
    """Refresh the oven door select from its reported boolean state."""
    attributes = {"door_open": False}
    device = Mock()
    device.device_type = 0x9B
    device.device_id = 1
    device.name = "Offline mapped attribute test"
    device.get_attribute.side_effect = attributes.get
    entity = MideaSelect(device, "door_select")
    entity.hass = Mock()
    entity.platform = Mock()
    assert entity.options == ["open", "close"]
    for opened, option in ((True, "open"), (False, "close")):
        attributes["door_open"] = opened
        with patch.object(entity, "schedule_update_if_running") as refresh:
            entity.update_state({"door_open": opened})
        refresh.assert_called_once_with()
        assert entity.current_option == option
        device.set_attribute.assert_not_called()
        entity.select_option(option)
        device.set_attribute.assert_called_once_with("door", option)
        device.set_attribute.reset_mock()


@pytest.mark.parametrize("control", GATED_CONTROLS, ids=_control_id)
def test_unrelated_updates_do_not_publish(
    control: tuple["MideaEntity", dict[str, bool], str],
) -> None:
    """Ignore reports that change neither the value nor availability."""
    entity = control[0]
    with patch.object(entity, "schedule_update_if_running") as refresh:
        entity.update_state({"unrelated": True})
    refresh.assert_not_called()


@pytest.mark.parametrize("control", GATED_CONTROLS, ids=_control_id)
def test_capability_updates_keep_shutdown_guard(
    control: tuple["MideaEntity", dict[str, bool], str],
) -> None:
    """Do not write new states when Home Assistant is stopping."""
    entity, _, capability = control
    entity.hass.is_stopping = True
    with patch.object(entity, "schedule_update_ha_state") as refresh:
        entity.update_state({capability: False})
    refresh.assert_not_called()
