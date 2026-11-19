"""Exercise generic platforms through Home Assistant's public APIs."""

from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_SENSORS,
    CONF_SWITCHES,
    STATE_OFF,
    STATE_ON,
    Platform,
)
from homeassistant.core import HomeAssistant
from midealan.device import DeviceType

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

from .conftest import setup_integration
from .ha import MockConfigEntry

pytestmark = pytest.mark.usefixtures(
    "enable_integration",
    "mock_device_selector",
    "simple_platforms",
)

ENTITY_PREFIX = "123456"


@pytest.fixture
def simple_platforms(
    monkeypatch: pytest.MonkeyPatch,
    mock_device: Mock,
) -> Generator[None]:
    """Install a small registry that spans every generic control platform."""
    entities = {
        "door": {
            "type": Platform.BINARY_SENSOR,
            "name": "Door",
            "default": True,
        },
        "action": {
            "type": Platform.BUTTON,
            "name": "Action",
            "default": True,
            "press_value": True,
        },
        "child_lock": {
            "type": Platform.LOCK,
            "name": "Child lock",
            "default": True,
        },
        "level": {
            "type": Platform.NUMBER,
            "name": "Level",
            "default": True,
            "min": 0,
            "max": 100,
            "step": 5,
        },
        "mode": {
            "type": Platform.SELECT,
            "name": "Mode",
            "default": True,
            "options": {1: "eco", 2: "boost"},
        },
        "eco_mode": {
            "type": Platform.SWITCH,
            "name": "Eco mode",
            "default": True,
        },
        "start": {
            "type": Platform.TIME,
            "name": "Start",
        },
    }
    monkeypatch.setitem(
        MIDEA_DEVICES,
        DeviceType.AC,
        {"name": "Air conditioner", "entities": entities},
    )
    mock_device.attributes.clear()
    mock_device.attributes.update(
        {
            "door": True,
            "child_lock": False,
            "level": 25,
            "mode": 1,
            "eco_mode": False,
            "start_hour": 8,
            "start_min": 30,
        },
    )
    platforms = [
        Platform.BINARY_SENSOR,
        Platform.BUTTON,
        Platform.LOCK,
        Platform.NUMBER,
        Platform.SELECT,
        Platform.SWITCH,
        Platform.TIME,
    ]
    with patch("custom_components.midea_ac_lan.ALL_PLATFORM", platforms):
        yield


async def test_generic_platform_states_services_and_push_updates(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Load generic platforms and use their states, services, and callbacks."""
    hass.config_entries.async_update_entry(
        config_entry,
        options={
            CONF_SENSORS: ["door"],
            CONF_SWITCHES: [
                "action",
                "child_lock",
                "level",
                "mode",
                "eco_mode",
                "start",
            ],
        },
    )
    await setup_integration(hass, config_entry)

    expected_states = {
        f"binary_sensor.{ENTITY_PREFIX}_door": STATE_ON,
        f"lock.{ENTITY_PREFIX}_child_lock": "unlocked",
        f"number.{ENTITY_PREFIX}_level": "25",
        f"select.{ENTITY_PREFIX}_mode": "eco",
        f"switch.{ENTITY_PREFIX}_eco_mode": STATE_OFF,
        f"time.{ENTITY_PREFIX}_start": "08:30:00",
    }
    for entity_id, expected in expected_states.items():
        assert hass.states.get(entity_id).state == expected
    assert hass.states.get(f"button.{ENTITY_PREFIX}_action") is not None
    assert mock_device.register_update.call_count == 7

    service_calls: list[tuple[str, str, str, dict[str, Any]]] = [
        ("button", "press", "action", {}),
        ("lock", "lock", "child_lock", {}),
        ("number", "set_value", "level", {"value": 30}),
        ("select", "select_option", "mode", {"option": "boost"}),
        ("switch", "turn_on", "eco_mode", {}),
        ("time", "set_value", "start", {"time": "09:45:00"}),
    ]
    for domain, service, key, data in service_calls:
        await hass.services.async_call(
            domain,
            service,
            {ATTR_ENTITY_ID: f"{domain}.{ENTITY_PREFIX}_{key}", **data},
            blocking=True,
        )
    await hass.async_block_till_done()

    assert hass.states.get(f"lock.{ENTITY_PREFIX}_child_lock").state == "locked"
    assert hass.states.get(f"number.{ENTITY_PREFIX}_level").state == "30.0"
    assert hass.states.get(f"select.{ENTITY_PREFIX}_mode").state == "boost"
    assert hass.states.get(f"switch.{ENTITY_PREFIX}_eco_mode").state == STATE_ON
    assert hass.states.get(f"time.{ENTITY_PREFIX}_start").state == "09:45:00"

    mock_device.notify_update({"door": False})
    await hass.async_block_till_done()
    assert hass.states.get(f"binary_sensor.{ENTITY_PREFIX}_door").state == STATE_OFF
