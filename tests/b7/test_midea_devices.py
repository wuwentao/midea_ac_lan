"""Tests for Midea B7 device registry integration."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock, call

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.b7 import DeviceAttributes

from custom_components.midea_ac_lan.button import MideaButton
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.number import MideaNumber

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def b7_entities() -> dict[DeviceAttributes, dict[str, object]]:
    """Return the B7 entity registry with its concrete type."""
    return cast(
        "dict[DeviceAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.B7]["entities"],
    )


def b7_device() -> Mock:
    """Build a minimal B7 device for generic entity tests."""
    device = Mock()
    device.device_type = DeviceType.B7
    device.device_id = 1
    device.name = "B7 test device"
    device.available = True
    device.get_attribute.return_value = None
    return device


def test_b7_registry_matches_released_library_attributes() -> None:
    """Expose every attribute shipped by midea-lan 2026.11.0."""
    entities = b7_entities()

    assert set(entities) == set(DeviceAttributes)
    expected_platforms = {
        Platform.SWITCH: {DeviceAttributes.lock},
        Platform.BUTTON: {
            DeviceAttributes.left_power,
            DeviceAttributes.right_power,
        },
        Platform.NUMBER: {
            DeviceAttributes.left_gear_set,
            DeviceAttributes.right_gear_set,
            DeviceAttributes.left_temp_set,
            DeviceAttributes.right_temp_set,
        },
        Platform.BINARY_SENSOR: {
            DeviceAttributes.gas_warn,
            DeviceAttributes.left_smart_bl,
            DeviceAttributes.right_smart_bl,
            DeviceAttributes.menu_mark,
        },
        Platform.SENSOR: {
            DeviceAttributes.left_status,
            DeviceAttributes.right_status,
            DeviceAttributes.left_gear,
            DeviceAttributes.right_gear,
            DeviceAttributes.left_work_mode,
            DeviceAttributes.right_work_mode,
            DeviceAttributes.left_temp,
            DeviceAttributes.right_temp,
            DeviceAttributes.left_surplus_hours,
            DeviceAttributes.left_surplus_minutes,
            DeviceAttributes.right_surplus_hours,
            DeviceAttributes.right_surplus_minutes,
            DeviceAttributes.left_work_hours,
            DeviceAttributes.left_work_minutes,
            DeviceAttributes.left_work_seconds,
            DeviceAttributes.right_work_hours,
            DeviceAttributes.right_work_minutes,
            DeviceAttributes.right_work_seconds,
            DeviceAttributes.error_code,
            DeviceAttributes.tips_code,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes


def test_b7_control_semantics_match_released_protocol() -> None:
    """Use momentary ignition buttons and optimistic setpoint controls."""
    entities = b7_entities()
    device = b7_device()

    for attribute in (DeviceAttributes.left_power, DeviceAttributes.right_power):
        config = entities[attribute]
        assert config["press_value"] is True
        MideaButton(device, attribute).press()

    for index, attribute in enumerate(
        (
            DeviceAttributes.left_gear_set,
            DeviceAttributes.right_gear_set,
            DeviceAttributes.left_temp_set,
            DeviceAttributes.right_temp_set,
        ),
        start=1,
    ):
        assert entities[attribute]["optimistic"] is True
        number = MideaNumber(device, attribute)
        number.set_native_value(index)
        assert number.native_value == index
        assert number.assumed_state

    assert device.set_attribute.call_args_list == [
        call(DeviceAttributes.left_power, True),
        call(DeviceAttributes.right_power, True),
        call(DeviceAttributes.left_gear_set, 1),
        call(DeviceAttributes.right_gear_set, 2),
        call(DeviceAttributes.left_temp_set, 3),
        call(DeviceAttributes.right_temp_set, 4),
    ]


def test_b7_sensor_state_classes_match_value_semantics() -> None:
    """Only expose measurement metadata for quantities HA can aggregate."""
    entities = b7_entities()
    protocol_codes = {
        DeviceAttributes.left_status,
        DeviceAttributes.right_status,
        DeviceAttributes.left_gear,
        DeviceAttributes.right_gear,
        DeviceAttributes.left_work_mode,
        DeviceAttributes.right_work_mode,
        DeviceAttributes.error_code,
        DeviceAttributes.tips_code,
    }

    for attribute in protocol_codes:
        assert "state_class" not in entities[attribute]


def test_b7_translation_keys_follow_shared_key_rules() -> None:
    """Use attribute keys except for the conflicting panel-lock meaning."""
    for attribute, config in b7_entities().items():
        expected = "b7_lock" if attribute is DeviceAttributes.lock else attribute.value
        assert config["translation_key"] == expected


def test_b7_translations_cover_every_locale_without_english_fallback() -> None:
    """Require localized entity names in every shipped locale."""
    entities = b7_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]

    for translation_file in translation_files:
        translations = json.loads(translation_file.read_text(encoding="utf-8"))[
            "entity"
        ]
        for attribute, config in entities.items():
            platform = cast("Platform", config["type"]).value
            translation_key = cast("str", config["translation_key"])
            name = translations[platform][translation_key]["name"].strip()
            assert name
            if (
                translation_file.stem != "en"
                and attribute is not DeviceAttributes.error_code
            ):
                assert name != english[platform][translation_key]["name"]
