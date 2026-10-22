"""Keep dishwasher status buttons and laundry cancellation compatible."""

# ruff: file-ignore[pytest-unittest-assertion]

import unittest
from unittest.mock import Mock, patch

from midea_ac_lan.button import MideaButton
from midea_ac_lan.midea_devices import MIDEA_DEVICES

LAUNDRY_TYPES = [
    device_type
    for device_type in (0xDB, 0xDC)
    if "cancel_appointment" in MIDEA_DEVICES[device_type]["entities"]
]


def device_mock(device_type: int) -> Mock:
    """Build an offline device with power and capabilities enabled.

    Returns
    -------
    Mock
        A device whose commands stay inside the test.

    """
    device = Mock()
    device.device_type = device_type
    device.device_id = 1
    device.name = "Offline button test"
    device.available = True
    device.get_attribute.return_value = True
    return device


class ButtonDispatchTests(unittest.TestCase):
    """Exercise the actual entity configs on both sides of the merge."""

    def test_dishwasher_status_commands(self) -> None:
        """Preserve all five dishwasher actions introduced by main."""
        commands = {
            "start": "work",
            "start_delayed": "order",
            "cancel": "cancel",
            "pause": "pause",
            "resume": "resume",
        }
        for key, expected in commands.items():
            with self.subTest(button=key):
                device = device_mock(0xE1)
                entity = MideaButton(device, key)
                entity.press()
                device.set_attribute.assert_called_once_with("status", expected)
                self.assertTrue(entity.available)
                device.get_attribute.return_value = False
                self.assertFalse(entity.available)

    def test_laundry_cancellation_preserves_false(self) -> None:
        """Cancellation writes the appointment flag without a status command."""
        self.assertTrue(LAUNDRY_TYPES)
        for device_type in LAUNDRY_TYPES:
            with self.subTest(device_type=device_type):
                device = device_mock(device_type)
                entity = MideaButton(device, "cancel_appointment")
                entity.press()
                device.set_attribute.assert_called_once_with("appointment", False)
                self.assertTrue(entity.available)
                device.get_attribute.return_value = False
                self.assertFalse(entity.available)

    def test_power_updates_refresh_dishwasher_buttons(self) -> None:
        """Power reports refresh button availability after the merge."""
        entity = MideaButton(device_mock(0xE1), "start")
        entity.hass = Mock()
        with patch.object(entity, "schedule_update_if_running") as refresh:
            entity.update_state({"power": False})
        self.assertEqual(refresh.call_args_list, [unittest.mock.call()])

    def test_capability_updates_refresh_laundry_buttons(self) -> None:
        """Reservation editability reports refresh the cancellation button."""
        for device_type in LAUNDRY_TYPES:
            with self.subTest(device_type=device_type):
                entity = MideaButton(
                    device_mock(device_type),
                    "cancel_appointment",
                )
                entity.hass = Mock()
                with patch.object(entity, "schedule_update_if_running") as refresh:
                    entity.update_state({"appointment_controls_available": False})
                refresh.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
