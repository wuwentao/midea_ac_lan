"""Refresh laundry controls when only SDK editability changes."""

# ruff: file-ignore[pytest-unittest-assertion]

import unittest
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock, patch

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


class ControlAvailabilityTests(unittest.TestCase):
    """Exercise configured controls without sending appliance commands."""

    def setUp(self) -> None:
        """Build every laundry control gated by an SDK capability."""
        self.controls: list[tuple[MideaEntity, dict[str, bool], str]] = []
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
                self.controls.append((entity, attributes, capability))
        self.assertTrue(self.controls)

    def test_capability_only_updates_publish_both_transitions(self) -> None:
        """Publish availability even when the control's own value is unchanged."""
        for entity, attributes, capability in self.controls:
            with self.subTest(entity=entity.entity_id):
                self.assertTrue(entity.available)
                for available in (False, True):
                    attributes[capability] = available
                    with patch.object(entity, "schedule_update_if_running") as refresh:
                        entity.update_state({capability: available})
                    refresh.assert_called_once_with()
                    self.assertEqual(entity.available, available)

    def test_unrelated_updates_do_not_publish(self) -> None:
        """Ignore reports that change neither the value nor availability."""
        for entity, _, _ in self.controls:
            with (
                self.subTest(entity=entity.entity_id),
                patch.object(entity, "schedule_update_if_running") as refresh,
            ):
                entity.update_state({"unrelated": True})
                refresh.assert_not_called()

    def test_capability_updates_keep_shutdown_guard(self) -> None:
        """Do not write new states when Home Assistant is stopping."""
        for entity, _, capability in self.controls:
            with self.subTest(entity=entity.entity_id):
                entity.hass.is_stopping = True
                with patch.object(entity, "schedule_update_ha_state") as refresh:
                    entity.update_state({capability: False})
                refresh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
