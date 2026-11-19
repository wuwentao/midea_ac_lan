"""Integration coverage for protocol-specific FD humidifier layouts."""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import call, patch

import pytest
import voluptuous as vol
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_SWITCHES,
    CONF_TYPE,
    Platform,
)
from midealan.const import DeviceType, ProtocolVersion
from midealan.devices.fd import DeviceAttributes, MideaFDDevice
from midealan.message import MessageType

from custom_components.midea_ac_lan.config_flow import MideaLanOptionsFlowHandler
from custom_components.midea_ac_lan.const import CONF_MODEL, DEVICES, DOMAIN
from custom_components.midea_ac_lan.humidifier import MideaFDHumidifier
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.select import MideaSelect
from custom_components.midea_ac_lan.switch import MideaSwitch

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def _build_device(subtype: int) -> MideaFDDevice:
    """Build an offline FD device for entity-level tests."""
    return MideaFDDevice(
        name="Test humidifier",
        device_id=1,
        ip_address="192.0.2.1",
        port=6444,
        token="AA",  # ruff: ignore[hardcoded-password-func-arg]
        key="BB",
        device_protocol=ProtocolVersion.V1,
        model="compatible_model",
        subtype=subtype,
        customize="",
    )


def _build_message(message_type: MessageType, body: bytearray) -> bytes:
    """Build a complete FD response message around a captured C8 body."""
    header = bytearray(
        [0xAA] + ([0x00] * 7) + [ProtocolVersion.V1] + [message_type],
    )
    return bytes(header + body + bytearray([0x00]))


def _process_lua_25_status(device: MideaFDDevice) -> None:
    """Process the complete Lua 25 C8 frame captured in issue 1115."""
    body = bytearray.fromhex(
        "c80110007f7f002d0000002d400201003b5a"
        "0000000000000000000000000000000000000000007f000080020000",
    )
    device.process_message(_build_message(MessageType.query, body))


def _process_lua_2024110101_status(device: MideaFDDevice) -> None:
    """Process the Lua 2024110101 C8 frame captured in issue 525."""
    body = bytearray.fromhex(
        "c80101277f7f00320006"
        "280000010000425c0040"
        "00000000000000000000"
        "00000000000000000000"
        "00001000000000000000",
    )
    device.process_message(_build_message(MessageType.notify1, body))


def test_wet_pad_drying_registry_uses_reported_capability() -> None:
    """Register wet-pad drying as an optional, capability-gated switch."""
    entities = cast(
        "dict[object, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.FD]["entities"],
    )
    assert entities[DeviceAttributes.wet_pad_dry] == {
        "type": Platform.SWITCH,
        "required_attribute": DeviceAttributes.wet_pad_dry,
        "available_value_attribute": DeviceAttributes.wet_pad_dry,
        "translation_key": "wet_pad_dry",
        "name": "Wet Pad Drying",
        "icon": "mdi:water-off-outline",
    }


def test_wet_pad_drying_name_exists_in_all_translations() -> None:
    """Require a localized wet-pad drying name in every shipped language."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        assert translation["entity"]["switch"]["wet_pad_dry"]["name"]


async def test_wet_pad_drying_option_requires_reported_capability() -> None:
    """Offer wet-pad drying only after a supporting status report."""
    entry = SimpleNamespace(
        data={
            CONF_TYPE: DeviceType.FD,
            CONF_DEVICE_ID: 1,
            CONF_IP_ADDRESS: "192.0.2.1",
            CONF_MODEL: "compatible_model",
        },
        options={},
    )

    lua_25 = _build_device(0)
    _process_lua_25_status(lua_25)
    handler = MideaLanOptionsFlowHandler(entry)
    handler.hass = SimpleNamespace(data={DOMAIN: {DEVICES: {1: lua_25}}})
    schema = (await handler.async_step_init())["data_schema"]
    with pytest.raises(vol.Invalid):
        schema({CONF_SWITCHES: [DeviceAttributes.wet_pad_dry]})

    lua_2024110101 = _build_device(7)
    _process_lua_2024110101_status(lua_2024110101)
    handler = MideaLanOptionsFlowHandler(entry)
    handler.hass = SimpleNamespace(data={DOMAIN: {DEVICES: {1: lua_2024110101}}})
    schema = (await handler.async_step_init())["data_schema"]
    validated = schema({CONF_SWITCHES: [DeviceAttributes.wet_pad_dry]})
    assert validated[CONF_SWITCHES] == [DeviceAttributes.wet_pad_dry]


def test_lua_25_entities_follow_hardware_verified_status() -> None:
    """Expose the modes, fan levels, and display state verified in issue 1115."""
    device = _build_device(0)
    _process_lua_25_status(device)

    humidifier = MideaFDHumidifier(device, "humidifier")
    fan = MideaSelect(device, DeviceAttributes.fan_speed)
    display = MideaSelect(device, DeviceAttributes.screen_display)

    assert humidifier.mode == "auto"
    assert humidifier.target_humidity == 45
    assert humidifier.available_modes == [
        "manual",
        "auto",
        "continuous",
        "living_room",
        "bed_room",
        "kitchen",
        "sleep",
    ]
    assert fan.current_option == "auto"
    assert fan.options == ["lowest", "low", "medium", "high", "auto"]
    assert display.current_option == "bright"
    assert display.options == ["bright", "off"]
    assert device.attributes[DeviceAttributes.wet_pad_dry] is None

    with patch.object(device, "set_attribute") as set_attribute:
        humidifier.set_mode("manual")
        humidifier.set_humidity(50)
        fan.select_option("high")
        display.select_option("off")
    assert set_attribute.call_args_list == [
        call("mode", "manual"),
        call("target_humidity", 50),
        call(DeviceAttributes.fan_speed, "high"),
        call(DeviceAttributes.screen_display, "off"),
    ]


def test_lua_2024110101_entities_follow_official_status() -> None:
    """Expose the U12 modes, fan levels, and display choices from issue 525."""
    device = _build_device(7)
    _process_lua_2024110101_status(device)

    humidifier = MideaFDHumidifier(device, "humidifier")
    fan = MideaSelect(device, DeviceAttributes.fan_speed)
    display = MideaSelect(device, DeviceAttributes.screen_display)
    wet_pad_drying = MideaSwitch(device, DeviceAttributes.wet_pad_dry)

    assert humidifier.mode == "manual"
    assert humidifier.target_humidity == 50
    assert humidifier.available_modes == ["manual", "sleep", "moist_skin"]
    assert fan.current_option == "low"
    assert fan.options == ["low", "medium", "high"]
    assert display.current_option == "dim"
    assert display.options == ["bright", "dim", "off"]
    assert wet_pad_drying.is_on

    with patch.object(device, "set_attribute") as set_attribute:
        humidifier.set_mode("sleep")
        humidifier.set_humidity(55)
        fan.select_option("high")
        display.select_option("off")
        wet_pad_drying.turn_off()
        wet_pad_drying.turn_on()
    assert set_attribute.call_args_list == [
        call("mode", "sleep"),
        call("target_humidity", 55),
        call(DeviceAttributes.fan_speed, "high"),
        call(DeviceAttributes.screen_display, "off"),
        call(attr=DeviceAttributes.wet_pad_dry, value=False),
        call(attr=DeviceAttributes.wet_pad_dry, value=True),
    ]
