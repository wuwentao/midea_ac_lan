"""Regression checks for button dispatch in ``midea_ac_lan.button``.

Covers the dishwasher status buttons (0xE1) kept compatible with ``main`` and
the laundry cancellation button shared by the washer (0xDB) and dryer (0xDC).
"""

import unittest.mock
from unittest.mock import Mock, patch

import pytest
from homeassistant.const import Platform

from custom_components.midea_ac_lan.button import MideaButton, async_setup_entry
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

from .helpers import DeviceFactory, InstallConfig, setup_context

# Both laundry device types register the same cancellation button; iterate over
# whichever of them exposes it so the washer and dryer stay covered together.
LAUNDRY_TYPES = [
    device_type
    for device_type in (0xDB, 0xDC)
    if "cancel_appointment" in MIDEA_DEVICES[device_type]["entities"]
]


def device_mock(device_type: int) -> Mock:
    """Build an offline device with power and capabilities enabled."""
    device = Mock()
    device.device_type = device_type
    device.device_id = 1
    device.name = "Offline button test"
    device.available = True
    device.get_attribute.return_value = True
    return device


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("start", "work"),
        ("start_delayed", "order"),
        ("cancel", "cancel"),
        ("pause", "pause"),
        ("resume", "resume"),
    ],
)
def test_dishwasher_status_commands(key: str, expected: str) -> None:
    """Preserve all five dishwasher actions introduced by main."""
    device = device_mock(0xE1)
    entity = MideaButton(device, key)
    entity.press()
    device.set_attribute.assert_called_once_with("status", expected)
    assert entity.available
    device.get_attribute.return_value = False
    assert not entity.available


@pytest.mark.parametrize("device_type", LAUNDRY_TYPES)
def test_laundry_cancellation_preserves_false(device_type: int) -> None:
    """Cancellation writes the appointment flag without a status command."""
    assert LAUNDRY_TYPES
    device = device_mock(device_type)
    entity = MideaButton(device, "cancel_appointment")
    entity.press()
    device.set_attribute.assert_called_once_with("appointment", False)
    assert entity.available
    device.get_attribute.return_value = False
    assert not entity.available


def test_power_updates_refresh_dishwasher_buttons() -> None:
    """Power reports refresh button availability after the merge."""
    entity = MideaButton(device_mock(0xE1), "start")
    entity.hass = Mock()
    with patch.object(entity, "schedule_update_if_running") as refresh:
        entity.update_state({"power": False})
    assert refresh.call_args_list == [unittest.mock.call()]


@pytest.mark.parametrize("device_type", LAUNDRY_TYPES)
def test_capability_updates_refresh_laundry_buttons(device_type: int) -> None:
    """Reservation editability reports refresh the cancellation button."""
    entity = MideaButton(device_mock(device_type), "cancel_appointment")
    entity.hass = Mock()
    with patch.object(entity, "schedule_update_if_running") as refresh:
        entity.update_state({"appointment_controls_available": False})
    refresh.assert_called_once_with()


async def test_async_setup_entry_filters_buttons(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only add supported, enabled buttons with their required capability."""
    install_config(
        {
            "default": {
                "type": Platform.BUTTON,
                "default": True,
                "press_value": True,
            },
            "selected": {"type": Platform.BUTTON, "press_value": True},
            "missing": {
                "type": Platform.BUTTON,
                "default": True,
                "required_attribute": "capability",
                "press_value": True,
            },
            "unsupported": {
                "type": Platform.BUTTON,
                "default": True,
                "models": ["OTHER"],
                "press_value": True,
            },
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    assert [item._entity_key for item in add_entities.call_args.args[0]] == [
        "default",
        "selected",
    ]


def test_button_availability_press_and_detached_update(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Gate on device power, send mapped values, and ignore detached updates."""
    install_config(
        {
            "start": {
                "type": Platform.BUTTON,
                "attribute": "command",
                "press_value": "start",
                "available_power_attribute": "power",
            },
            "pause": {"type": Platform.BUTTON, "press_status": "pause"},
        },
    )
    device, values = device_factory(attributes={"power": False})
    start = MideaButton(device, "start")
    assert not start.available
    values["power"] = True
    assert start.available
    start.press()
    MideaButton(device, "pause").press()
    assert device.set_attribute.call_args_list == [
        unittest.mock.call("command", "start"),
        unittest.mock.call("status", "pause"),
    ]
    device.available = False
    assert not start.available

    start.schedule_update_if_running = Mock()
    start.update_state({"power": False})
    start.schedule_update_if_running.assert_not_called()
