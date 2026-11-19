"""Integration coverage for protocol-specific FD humidifier layouts."""

from unittest.mock import call, patch

from midealan.const import ProtocolVersion
from midealan.devices.fd import DeviceAttributes, MideaFDDevice
from midealan.message import MessageType

from custom_components.midea_ac_lan.humidifier import MideaFDHumidifier
from custom_components.midea_ac_lan.select import MideaSelect


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


def test_lua_25_entities_follow_hardware_verified_status() -> None:
    """Expose the modes, fan levels, and display state verified in issue 1115."""
    device = _build_device(0)
    body = bytearray.fromhex(
        "c80110007f7f002d0000002d400201003b5a"
        "0000000000000000000000000000000000000000007f000080020000",
    )
    device.process_message(_build_message(MessageType.query, body))

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
    body = bytearray.fromhex(
        "c80101277f7f00320006"
        "280000010000425c0040"
        "00000000000000000000"
        "00000000000000000000"
        "00001000000000000000",
    )
    device.process_message(_build_message(MessageType.notify1, body))

    humidifier = MideaFDHumidifier(device, "humidifier")
    fan = MideaSelect(device, DeviceAttributes.fan_speed)
    display = MideaSelect(device, DeviceAttributes.screen_display)

    assert humidifier.mode == "manual"
    assert humidifier.target_humidity == 50
    assert humidifier.available_modes == ["manual", "sleep", "moist_skin"]
    assert fan.current_option == "low"
    assert fan.options == ["low", "medium", "high"]
    assert display.current_option == "dim"
    assert display.options == ["bright", "dim", "off"]

    with patch.object(device, "set_attribute") as set_attribute:
        humidifier.set_mode("sleep")
        humidifier.set_humidity(55)
        fan.select_option("high")
        display.select_option("off")
    assert set_attribute.call_args_list == [
        call("mode", "sleep"),
        call("target_humidity", 55),
        call(DeviceAttributes.fan_speed, "high"),
        call(DeviceAttributes.screen_display, "off"),
    ]
