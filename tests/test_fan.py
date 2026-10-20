"""Tests for the HA fan glue; wire mappings are tested in midea-lan."""

import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from midealan.const import ProtocolVersion
from midealan.devices.fa import MideaFADevice

from custom_components.midea_ac_lan.const import DEVICES, DOMAIN
from custom_components.midea_ac_lan.fan import MideaFAFan, async_setup_entry


def make_device(model: str = "BGF10000", subtype: int = 15) -> MideaFADevice:
    """Create an offline device with no connection or credentials.

    Returns:
        A real protocol device that has not opened a connection.

    """
    return MideaFADevice(
        name="Test fan",
        device_id=1,
        ip_address="192.0.2.1",
        port=6444,
        token="",
        key="",
        device_protocol=ProtocolVersion.V3,
        model=model,
        subtype=subtype,
        customize='{"speed_count": 12}',
    )


class TestFAFanDelegation(unittest.TestCase):
    """Expose library capabilities without duplicating protocol mappings."""

    def setUp(self) -> None:
        """Create a fresh device and entity."""
        self.device = make_device()
        self.fan = MideaFAFan(self.device, "fan")

    def test_presets_come_from_library(self) -> None:
        """Forward library options and decoded state without hardcoded lists."""
        presets = ["normal", "forest", "sleep_1"]
        with patch.object(
            MideaFADevice,
            "preset_modes",
            new_callable=PropertyMock,
            return_value=presets,
        ):
            assert self.fan.preset_modes == presets
        with patch.object(self.device, "get_attribute", return_value="forest"):
            assert self.fan.preset_mode == "forest"
        with patch.object(self.device, "get_attribute", return_value=None):
            assert self.fan.percentage is None

    def test_set_preset_delegates(self) -> None:
        """Let the library construct the complete mode/speed command."""
        with patch.object(self.device, "set_attribute") as setter:
            self.fan.set_preset_mode("forest")
        setter.assert_called_once_with(attr="mode", value="forest")

    def test_turn_on_delegates(self) -> None:
        """Leave combined preset and speed precedence to the library."""
        with patch.object(self.device, "turn_on") as turn_on:
            self.fan.turn_on(percentage=50, preset_mode="forest")
        turn_on.assert_called_once_with(fan_speed=6, mode="forest")
        with patch.object(self.device, "turn_on") as turn_on:
            self.fan.turn_on()
        turn_on.assert_called_once_with(fan_speed=None, mode=None)

    def test_set_speed_delegates(self) -> None:
        """Convert percentage using the device speed count."""
        with patch.object(self.device, "set_attribute") as setter:
            self.fan.set_percentage(50)
        setter.assert_called_once_with(attr="fan_speed", value=6)


class TestFanSelection(unittest.IsolatedAsyncioTestCase):
    """Keep model-specific display labels isolated from other FA devices."""

    async def test_only_matching_model_gets_translation_key(self) -> None:
        """Use the generic entity everywhere and specialize only the labels."""
        for model, subtype, key in [
            ("BGF10000", 15, "bgf10000"),
            ("BGF10000", 14, None),
            ("56000211", 15, None),
        ]:
            with self.subTest(model=model, subtype=subtype):
                device = make_device(model, subtype)
                hass = MagicMock(spec=HomeAssistant)
                hass.data = {DOMAIN: {DEVICES: {1: device}}}
                entry = MagicMock(spec=ConfigEntry)
                entry.data = {CONF_DEVICE_ID: 1}
                entry.options = {}
                add = Mock()
                await async_setup_entry(hass, entry, add)
                entity = add.call_args.args[0][0]
                assert type(entity) is MideaFAFan
                assert entity.translation_key == key
                assert entity.preset_modes == device.preset_modes
