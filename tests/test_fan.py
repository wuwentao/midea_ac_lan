"""Regression tests for BGF10000 presets using captured FA responses."""

import unittest
from unittest.mock import MagicMock, Mock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from midealan.const import ProtocolVersion
from midealan.devices.fa import MideaFADevice

from custom_components.midea_ac_lan.const import DEVICES, DOMAIN
from custom_components.midea_ac_lan.fan import (
    MideaBGF10000Fan,
    MideaFAFan,
    async_setup_entry,
)

FULL_PERCENTAGE = 100
COMFORT_MODE_CODE = 4


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


class TestBGF10000Presets(unittest.TestCase):
    """Exercise the HA entity against the pinned protocol library."""

    def setUp(self) -> None:
        """Create a fresh entity for each test."""
        self.device = make_device()
        self.fan = MideaBGF10000Fan(self.device, "fan")

    def test_captured_responses(self) -> None:
        """Decode all seven App presets from captured query responses."""
        samples = [
            ("forest", "0901", "98"),
            ("beach", "0902", "97"),
            ("countryside", "0903", "96"),
            ("baby", "0701", "9a"),
            ("sleep_1", "0702", "99"),
            ("sleep_2", "0703", "98"),
            ("strong", "130c", "83"),
            ("normal", "030c", "93"),
        ]
        for preset, mode_speed, checksum in samples:
            with self.subTest(preset=preset):
                raw = bytes.fromhex(
                    "aa1efa0000000000000300000000"
                    f"{mode_speed}00004300000000000000ffff0200{checksum}",
                )
                self.device.process_message(raw)
                assert self.fan.preset_mode == preset
                if preset not in {"normal", "strong"}:
                    assert self.fan.percentage is None
                else:
                    assert self.fan.percentage == FULL_PERCENTAGE

    def test_presets_send_one_combined_command(self) -> None:
        """Send both fields, also when turn_on contains a percentage."""
        presets = [
            ("normal", 1, None),
            ("forest", 4, 1),
            ("beach", 4, 2),
            ("countryside", 4, 3),
            ("baby", 3, 1),
            ("sleep_1", 3, 2),
            ("sleep_2", 3, 3),
            ("strong", 9, 12),
        ]
        assert self.fan.preset_modes == [item[0] for item in presets]
        for preset, mode, speed in presets:
            for turn_on in (False, True):
                with (
                    self.subTest(preset=preset, turn_on=turn_on),
                    patch.object(self.device, "build_send") as send,
                ):
                    if turn_on:
                        self.fan.turn_on(percentage=100, preset_mode=preset)
                    else:
                        self.fan.set_preset_mode(preset)
                    send.assert_called_once()
                    message = send.call_args.args[0]
                    assert message.mode == mode
                    assert message.fan_speed == speed
                    assert message.power
                    if speed is not None:
                        assert message.body[5] == speed

    def test_speed_selects_normal_mode(self) -> None:
        """Use the customized range and explicitly leave submode presets."""
        for percentage, speed in [(25, 3), (50, 6), (100, 12)]:
            with (
                self.subTest(percentage=percentage),
                patch.object(self.device, "build_send") as send,
            ):
                self.fan.set_percentage(percentage)
                message = send.call_args.args[0]
                assert (message.mode, message.fan_speed) == (1, speed)

    def test_plain_turn_on_preserves_mode(self) -> None:
        """Avoid replacing the mode or speed on a plain power command."""
        with patch.object(self.device, "build_send") as send:
            self.fan.turn_on()
        message = send.call_args.args[0]
        assert message.mode is None
        assert message.fan_speed is None
        assert message.power

    def test_turn_on_with_speed(self) -> None:
        """Apply a normal speed when turn_on explicitly requests one."""
        with patch.object(self.device, "build_send") as send:
            self.fan.turn_on(percentage=50)
        message = send.call_args.args[0]
        assert (message.mode, message.fan_speed) == (1, 6)
        assert message.power

    def test_unknown_submode(self) -> None:
        """Avoid guessing a preset for an unrecognized submode."""
        self.device.process_message(
            bytes.fromhex(
                "aa1efa0000000000000300000000090400004300000000000000ffff020095",
            ),
        )
        assert self.fan.preset_mode is None


class TestFanSelection(unittest.IsolatedAsyncioTestCase):
    """Keep the new adapter isolated to the confirmed model and subtype."""

    async def test_model_and_subtype_guard(self) -> None:
        """Use generic FA entities for every nonmatching combination."""
        for model, subtype, expected in [
            ("BGF10000", 15, MideaBGF10000Fan),
            ("BGF10000", 14, MideaFAFan),
            ("56000211", 15, MideaFAFan),
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
                assert type(add.call_args.args[0][0]) is expected
                if expected is MideaFAFan:
                    entity = add.call_args.args[0][0]
                    assert entity.preset_modes == device.preset_modes
                    with patch.object(device, "build_send") as send:
                        entity.set_preset_mode("comfort")
                    assert send.call_args.args[0].mode == COMFORT_MODE_CODE
                    assert send.call_args.args[0].fan_speed is None
