"""Tests for E2 device entity configuration."""

from typing import cast

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.e2 import DeviceAttributes as E2Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES


def test_eplus_switch_config() -> None:
    """Expose E2 Capacity Plus as a switch with its own translation."""
    entities = cast(
        "dict[E2Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.E2]["entities"],
    )

    assert entities[E2Attributes.eplus] == {
        "type": Platform.SWITCH,
        "translation_key": "eplus",
        "name": "Capacity Plus",
        "icon": "mdi:water-plus",
    }
