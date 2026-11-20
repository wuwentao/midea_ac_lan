"""Tests for the 0xF1 device registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfTemperature
from midealan.const import DeviceType
from midealan.devices.f1 import DeviceAttributes
from midealan.devices.f1 import message as f1_message

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def f1_entities() -> dict[DeviceAttributes, dict[str, Any]]:
    """Return the 0xF1 registry mapping with precise test typing."""
    return cast(
        "dict[DeviceAttributes, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.F1]["entities"],
    )


def test_f1_registry_matches_released_library() -> None:
    """Expose every released F1 attribute on its matching HA platform."""
    entities = f1_entities()

    assert set(entities) == set(DeviceAttributes)
    expected_platforms = {
        Platform.SWITCH: {DeviceAttributes.power},
        Platform.NUMBER: {
            DeviceAttributes.speed,
            DeviceAttributes.set_work_temp,
            DeviceAttributes.set_keep_warm_temp,
            DeviceAttributes.set_work_time,
            DeviceAttributes.set_keep_warm_time,
            DeviceAttributes.appoint_time,
            DeviceAttributes.code_id,
            DeviceAttributes.work_mode,
        },
        Platform.SENSOR: {
            DeviceAttributes.response_type,
            DeviceAttributes.work_status,
            DeviceAttributes.step_status,
            DeviceAttributes.work_stage,
            DeviceAttributes.lid_status,
            DeviceAttributes.cup_status,
            DeviceAttributes.current_time,
            DeviceAttributes.current_temp,
            DeviceAttributes.error_code,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes

    assert entities[DeviceAttributes.power]["default"] is True


def test_f1_number_controls_match_library_ranges() -> None:
    """Keep HA number limits synchronized with midea-lan 2026.11.0."""
    entities = f1_entities()
    expected = {
        DeviceAttributes.speed: (f1_message.SPEED_LOW, f1_message.SPEED_HIGH),
        DeviceAttributes.set_work_temp: (
            f1_message.TEMP_LOW,
            f1_message.TEMP_HIGH,
        ),
        DeviceAttributes.set_keep_warm_temp: (
            f1_message.TEMP_LOW,
            f1_message.TEMP_HIGH,
        ),
        DeviceAttributes.set_work_time: (
            f1_message.TIME_16_LOW,
            f1_message.TIME_16_HIGH,
        ),
        DeviceAttributes.set_keep_warm_time: (
            f1_message.WARM_TIME_LOW,
            f1_message.WARM_TIME_HIGH,
        ),
        DeviceAttributes.appoint_time: (
            f1_message.TIME_16_LOW,
            f1_message.TIME_16_HIGH,
        ),
        DeviceAttributes.code_id: (
            f1_message.CODE_ID_LOW,
            f1_message.CODE_ID_HIGH,
        ),
        DeviceAttributes.work_mode: (
            f1_message.MODE_LOW,
            f1_message.MODE_HIGH,
        ),
    }

    for attribute, (minimum, maximum) in expected.items():
        config = entities[attribute]
        assert config["min"] == minimum
        assert config["max"] == maximum
        assert config["step"] == 1

    for attribute in (
        DeviceAttributes.set_work_temp,
        DeviceAttributes.set_keep_warm_temp,
    ):
        config = entities[attribute]
        assert config["device_class"] is NumberDeviceClass.TEMPERATURE
        assert config["unit"] == UnitOfTemperature.CELSIUS


def test_f1_sensor_metadata_matches_library_values() -> None:
    """Expose translated enums and temperature metadata for F1 telemetry."""
    entities = f1_entities()
    expected_enum_values = {
        DeviceAttributes.response_type: set(f1_message.RESPONSE_NAMES.values()),
        DeviceAttributes.lid_status: set(f1_message.LID_STATUS_NAMES.values()),
        DeviceAttributes.cup_status: set(f1_message.CUP_STATUS_NAMES.values()),
    }
    for attribute, values in expected_enum_values.items():
        config = entities[attribute]
        assert config["device_class"] is SensorDeviceClass.ENUM
        assert config["options"] == {value: value for value in values}

    current_temp = entities[DeviceAttributes.current_temp]
    assert current_temp["device_class"] is SensorDeviceClass.TEMPERATURE
    assert current_temp["unit"] == UnitOfTemperature.CELSIUS
    assert current_temp["state_class"] is SensorStateClass.MEASUREMENT


def test_f1_translation_keys_follow_shared_key_rules() -> None:
    """Reuse shared keys except for the conflicting response enum."""
    entities = f1_entities()

    for attribute, config in entities.items():
        expected_key = {
            DeviceAttributes.current_temp: "current_temperature",
            DeviceAttributes.response_type: "f1_response_type",
        }.get(attribute, attribute.value)
        assert config["translation_key"] == expected_key


def test_f1_translations_cover_every_locale_without_english_fallback() -> None:
    """Require localized F1 names and enum states in every shipped locale."""
    entities = f1_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]
    new_keys = {
        Platform.NUMBER: {
            "speed",
            "set_work_temp",
            "set_keep_warm_temp",
            "set_work_time",
            "set_keep_warm_time",
            "appoint_time",
            "code_id",
            "work_mode",
        },
        Platform.SENSOR: {
            "f1_response_type",
            "step_status",
            "lid_status",
            "cup_status",
            "current_time",
        },
    }

    for translation_file in translation_files:
        translations = json.loads(translation_file.read_text(encoding="utf-8"))[
            "entity"
        ]
        for config in entities.values():
            platform = cast("Platform", config["type"])
            translation_key = cast("str", config["translation_key"])
            translation = translations[platform][translation_key]
            assert translation["name"].strip()
            if translation_file.stem != "en" and translation_key in new_keys.get(
                platform,
                set(),
            ):
                assert translation["name"] != english[platform][translation_key]["name"]
            for option in config.get("options", {}).values():
                state = translation["state"][option]
                assert state.strip()
                if translation_file.stem != "en":
                    assert state != english[platform][translation_key]["state"][option]
