"""Exercise the optional E1 controls through Home Assistant."""

from unittest.mock import Mock, call, patch

import pytest
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_SWITCHES,
    CONF_TYPE,
    STATE_OFF,
    STATE_ON,
    Platform,
)
from homeassistant.core import HomeAssistant
from midealan.device import DeviceType

from tests.conftest import TEST_DEVICE_ID, setup_integration
from tests.ha import MockConfigEntry

pytestmark = pytest.mark.usefixtures("enable_integration", "mock_device_selector")

DRY = f"switch.{TEST_DEVICE_ID}_dry_setting"
STORAGE_TIME = f"number.{TEST_DEVICE_ID}_storage_set_time"
CONTROLS = ["dry_setting", "storage_set_time"]


@pytest.mark.parametrize("supported", [True, False])
async def test_e1_extended_controls_follow_device_support_and_opt_in(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_device: Mock,
    supported: bool,
) -> None:
    """Offer the controls after opt-in only when the driver reports support."""
    hass.config_entries.async_update_entry(
        config_entry,
        data={**config_entry.data, CONF_TYPE: DeviceType.E1},
    )
    mock_device.device_type = DeviceType.E1
    if supported:
        mock_device.attributes.update(dry_setting=False, storage_set_time=0)

    with patch(
        "custom_components.midea_ac_lan.ALL_PLATFORM",
        [Platform.SWITCH, Platform.NUMBER],
    ):
        await setup_integration(hass, config_entry)
        assert hass.states.get(DRY) is None
        assert hass.states.get(STORAGE_TIME) is None

        hass.config_entries.async_update_entry(
            config_entry,
            options={CONF_SWITCHES: CONTROLS},
        )
        await hass.async_block_till_done()

    if not supported:
        assert hass.states.get(DRY) is None
        assert hass.states.get(STORAGE_TIME) is None
        return

    dry = hass.states.get(DRY)
    storage_time = hass.states.get(STORAGE_TIME)
    assert dry is not None
    assert dry.state == STATE_OFF
    assert storage_time is not None
    assert float(storage_time.state) == pytest.approx(0)

    await hass.services.async_call(
        "number",
        "set_value",
        {ATTR_ENTITY_ID: STORAGE_TIME, "value": 72},
        blocking=True,
    )
    await hass.services.async_call(
        "switch",
        "turn_on",
        {ATTR_ENTITY_ID: DRY},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert mock_device.set_attribute.call_args_list == [
        call("storage_set_time", 72),
        call(attr="dry_setting", value=True),
    ]
    assert hass.states.get(DRY).state == STATE_ON
    assert float(hass.states.get(STORAGE_TIME).state) == pytest.approx(72)
