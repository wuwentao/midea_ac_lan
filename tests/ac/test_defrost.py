"""Exercise the AC defrost sensor through Home Assistant."""

from unittest.mock import Mock

import pytest
import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import (
    CONF_SENSORS,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from midealan.devices.ac import DeviceAttributes as ACAttributes

from custom_components.midea_ac_lan.const import DOMAIN
from tests.conftest import TEST_DEVICE_ID, setup_integration
from tests.ha import MockConfigEntry

pytestmark = pytest.mark.usefixtures(
    "enable_integration",
    "mock_device_selector",
    "binary_sensor_platform",
)

DEFROST = ACAttributes.defrosting.value
ENTITY_ID = f"binary_sensor.{TEST_DEVICE_ID}_{DEFROST}"


@pytest.fixture
def binary_sensor_platform(monkeypatch: pytest.MonkeyPatch) -> None:
    """Load the real binary sensor platform with the original AC registry."""
    monkeypatch.setattr(
        "custom_components.midea_ac_lan.ALL_PLATFORM",
        [Platform.BINARY_SENSOR],
    )


@pytest.mark.parametrize("report", [{DEFROST: False}, {DEFROST: None}, {}])
async def test_defrost_opt_in(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
    report: dict[str, bool | None],
) -> None:
    """Offer defrost only after a known report and require explicit selection."""
    mock_device.attributes.update(report)
    await setup_integration(hass, config_entry)
    assert hass.states.get(ENTITY_ID) is None

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    schema = result["data_schema"]
    if report.get(DEFROST) is False:
        assert schema({CONF_SENSORS: [DEFROST]})[CONF_SENSORS] == [DEFROST]
    else:
        with pytest.raises(vol.Invalid):
            schema({CONF_SENSORS: [DEFROST]})


async def test_selected_defrost_state_and_reconnection(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Preserve the entity identity and distinguish unknown from inactive."""
    mock_device.attributes[DEFROST] = None
    hass.config_entries.async_update_entry(
        config_entry,
        options={CONF_SENSORS: [DEFROST]},
    )
    await setup_integration(hass, config_entry)

    registry_entry = er.async_get(hass).async_get(ENTITY_ID)
    assert registry_entry is not None
    assert registry_entry.unique_id == f"{DOMAIN}.{TEST_DEVICE_ID}_{DEFROST}"
    assert registry_entry.original_device_class == BinarySensorDeviceClass.RUNNING
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["data_schema"]({})[CONF_SENSORS] == [DEFROST]

    for value, expected in ((False, STATE_OFF), (True, STATE_ON), (False, STATE_OFF)):
        mock_device.notify_update({DEFROST: value})
        await hass.async_block_till_done()
        assert hass.states.get(ENTITY_ID).state == expected

    mock_device.notify_update({"available": False})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE
    mock_device.notify_update({"available": True, DEFROST: True})
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_ON


async def test_selected_defrost_missing_attribute(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
) -> None:
    """Skip a saved defrost entity when the device has no backing key."""
    assert DEFROST not in mock_device.attributes
    hass.config_entries.async_update_entry(
        config_entry,
        options={CONF_SENSORS: [DEFROST]},
    )
    await setup_integration(hass, config_entry)

    assert hass.states.get(ENTITY_ID) is None
    assert er.async_get(hass).async_get(ENTITY_ID) is None
