"""Exercise switch entities through HA services, state and lifecycle APIs."""

from unittest.mock import Mock

import pytest
import voluptuous as vol
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_RESTORED,
    CONF_SWITCHES,
    EVENT_HOMEASSISTANT_STOP,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.midea_ac_lan.const import DEVICES, DOMAIN

from .conftest import TEST_DEVICE_ID, TEST_MAC, setup_integration
from .ha import MockConfigEntry

pytestmark = pytest.mark.usefixtures(
    "enable_integration",
    "mock_device_selector",
    "switch_platform",
)

ENTITY_ID = f"switch.{TEST_DEVICE_ID}_eco_mode"


async def test_switch_setup_service_push_and_unload(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Register the entity and device, execute services, push state, and unload."""
    hass.config_entries.async_update_entry(
        config_entry,
        options={CONF_SWITCHES: ["eco_mode"]},
    )
    await setup_integration(hass, config_entry)
    assert config_entry.state is ConfigEntryState.LOADED
    assert hass.states.get(ENTITY_ID).state == STATE_OFF
    assert hass.states.get(ENTITY_ID).attributes["friendly_name"]
    mock_device.open.assert_called_once_with()
    mock_device.register_update.assert_called_once()

    entity = er.async_get(hass).async_get(ENTITY_ID)
    assert entity.unique_id == f"{DOMAIN}.{TEST_DEVICE_ID}_eco_mode"
    assert entity.config_entry_id == config_entry.entry_id
    device = dr.async_get(hass).async_get(entity.device_id)
    assert device.identifiers == {(DOMAIN, str(TEST_DEVICE_ID))}
    assert (dr.CONNECTION_NETWORK_MAC, TEST_MAC) in device.connections
    assert device.manufacturer == "Midea"

    for service, expected in (("turn_on", STATE_ON), ("turn_off", STATE_OFF)):
        await hass.services.async_call(
            "switch",
            service,
            {ATTR_ENTITY_ID: ENTITY_ID},
            blocking=True,
        )
        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == expected
    assert mock_device.set_attribute.call_count == 2
    mock_device.set_attribute.assert_called_with(attr="eco_mode", value=False)

    mock_device.notify_update({"eco_mode": True})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_ON
    mock_device.notify_update({"available": False})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE
    mock_device.notify_update({"available": True})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_ON

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
    assert TEST_DEVICE_ID not in hass.data[DOMAIN][DEVICES]
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE
    assert hass.states.get(ENTITY_ID).attributes[ATTR_RESTORED]
    mock_device.unregister_update.assert_called_once()
    mock_device.close.assert_called_once_with()
    mock_device.notify_update({"eco_mode": False})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE


async def test_switch_opt_in_and_option_reload(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Optional switches appear after a real options update reloads the entry."""
    await setup_integration(hass, config_entry)
    assert hass.states.get(ENTITY_ID) is None
    hass.config_entries.async_update_entry(
        config_entry,
        options={CONF_SWITCHES: ["eco_mode"]},
    )
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_OFF
    assert mock_device.open.call_count == 2
    mock_device.close.assert_called_once()


async def test_shutdown_closes_device(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """The stop event closes sockets even without a config entry unload."""
    await setup_integration(hass, config_entry)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()
    mock_device.close.assert_called_once_with()


async def test_integration_service_schema(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Run custom services through HA's schema validation and service registry."""
    await setup_integration(hass, config_entry)
    await hass.services.async_call(
        DOMAIN,
        "set_attribute",
        {"device_id": str(TEST_DEVICE_ID), "attribute": "eco_mode", "value": True},
        blocking=True,
    )
    mock_device.set_attribute.assert_called_once_with(attr="eco_mode", value=True)
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN,
            "set_attribute",
            {
                "device_id": TEST_DEVICE_ID,
                "attribute": "not_an_attribute",
                "value": True,
            },
            blocking=True,
        )
    mock_device.set_attribute.assert_called_once()
    await hass.services.async_call(
        DOMAIN,
        "send_command",
        {"device_id": TEST_DEVICE_ID, "cmd_type": 2, "cmd_body": "0102"},
        blocking=True,
    )
    mock_device.send_command.assert_called_once_with(2, bytearray([1, 2]))
