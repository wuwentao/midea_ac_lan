"""Tests for the 0xE9 device registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from midealan.const import DeviceType
from midealan.devices.e9 import DeviceAttributes
from midealan.devices.e9 import message as e9_message

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def e9_entities() -> dict[DeviceAttributes, dict[str, Any]]:
    """Return the 0xE9 registry mapping with precise test typing."""
    return cast(
        "dict[DeviceAttributes, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.E9]["entities"],
    )


def test_e9_registry_matches_released_library() -> None:
    """Expose every currently retrievable E9 attribute on its HA platform."""
    entities = e9_entities()

    # midea-lan 2026.11.0 decodes product_volume from query-info (0x51), but
    # its polling path only sends query-status (0x52), so it cannot supply that
    # value to Home Assistant until a future library release adds 0x51 polling.
    assert set(entities) == set(DeviceAttributes) - {DeviceAttributes.product_volume}
    expected_platforms = {
        Platform.NUMBER: {
            DeviceAttributes.control_cmd_code,
            DeviceAttributes.volume,
            DeviceAttributes.color,
            DeviceAttributes.dosing,
            DeviceAttributes.work_status,
            DeviceAttributes.time_cuisine_min,
            DeviceAttributes.time_cuisine_hr,
            DeviceAttributes.time_reserve_min,
            DeviceAttributes.time_reserve_hr,
            DeviceAttributes.bake_temperature,
        },
        Platform.SENSOR: {
            DeviceAttributes.response_type,
            DeviceAttributes.work_stage,
            DeviceAttributes.bottom_temperature,
            DeviceAttributes.time_work_min,
            DeviceAttributes.time_work_hr,
            DeviceAttributes.time_warm_min,
            DeviceAttributes.time_warm_hr,
            DeviceAttributes.error_code,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes

    response = entities[DeviceAttributes.response_type]
    assert response["device_class"] is SensorDeviceClass.ENUM
    assert response["options"] == {
        value: value for value in e9_message.RESPONSE_NAMES.values()
    }


def test_e9_number_controls_match_library_ranges() -> None:
    """Keep HA number limits synchronized with midea-lan 2026.11.0."""
    entities = e9_entities()
    expected = {
        DeviceAttributes.control_cmd_code: (
            e9_message.CMD_CODE_LOW,
            e9_message.CMD_CODE_HIGH,
            None,
        ),
        DeviceAttributes.volume: (
            e9_message.VOLUME_LOW,
            e9_message.VOLUME_HIGH,
            None,
        ),
        DeviceAttributes.color: (
            e9_message.COLOR_LOW,
            e9_message.COLOR_HIGH,
            None,
        ),
        DeviceAttributes.dosing: (
            e9_message.DOSING_LOW,
            e9_message.DOSING_HIGH,
            None,
        ),
        DeviceAttributes.work_status: (
            e9_message.WORK_STATUS_LOW,
            e9_message.WORK_STATUS_HIGH,
            None,
        ),
        DeviceAttributes.time_cuisine_min: (
            e9_message.TIME_MIN_LOW,
            e9_message.TIME_MIN_HIGH,
            UnitOfTime.MINUTES,
        ),
        DeviceAttributes.time_cuisine_hr: (
            e9_message.TIME_HR_LOW,
            e9_message.TIME_HR_HIGH,
            UnitOfTime.HOURS,
        ),
        DeviceAttributes.time_reserve_min: (
            e9_message.TIME_MIN_LOW,
            e9_message.TIME_MIN_HIGH,
            UnitOfTime.MINUTES,
        ),
        DeviceAttributes.time_reserve_hr: (
            e9_message.TIME_HR_LOW,
            e9_message.TIME_HR_HIGH,
            UnitOfTime.HOURS,
        ),
        DeviceAttributes.bake_temperature: (
            e9_message.BAKE_TEMPERATURE_LOW,
            e9_message.BAKE_TEMPERATURE_HIGH,
            UnitOfTemperature.CELSIUS,
        ),
    }

    for attribute, (minimum, maximum, unit) in expected.items():
        config = entities[attribute]
        assert config["min"] == minimum
        assert config["max"] == maximum
        assert config["step"] == 1
        if unit is None:
            assert "unit" not in config
        else:
            assert config["unit"] == unit

    assert (
        entities[DeviceAttributes.bake_temperature]["device_class"]
        is NumberDeviceClass.TEMPERATURE
    )


def test_e9_sensor_metadata() -> None:
    """Expose temperature and duration telemetry with native HA metadata."""
    entities = e9_entities()
    bottom_temperature = entities[DeviceAttributes.bottom_temperature]
    assert bottom_temperature["device_class"] is SensorDeviceClass.TEMPERATURE
    assert bottom_temperature["unit"] == UnitOfTemperature.CELSIUS
    assert bottom_temperature["state_class"] is SensorStateClass.MEASUREMENT

    durations = {
        DeviceAttributes.time_work_hr: UnitOfTime.HOURS,
        DeviceAttributes.time_work_min: UnitOfTime.MINUTES,
        DeviceAttributes.time_warm_hr: UnitOfTime.HOURS,
        DeviceAttributes.time_warm_min: UnitOfTime.MINUTES,
    }
    for attribute, unit in durations.items():
        config = entities[attribute]
        assert config["device_class"] is SensorDeviceClass.DURATION
        assert config["unit"] == unit
        assert config["state_class"] is SensorStateClass.MEASUREMENT


def test_e9_translation_keys_follow_shared_key_rules() -> None:
    """Use attribute names unless a same-platform semantic collision exists."""
    entities = e9_entities()

    for attribute in set(DeviceAttributes) - {DeviceAttributes.product_volume}:
        expected_key = (
            "e9_volume" if attribute is DeviceAttributes.volume else attribute.value
        )
        assert entities[attribute]["translation_key"] == expected_key


def test_e9_translations_cover_every_locale_without_english_fallback() -> None:
    """Require localized names and response states in every shipped locale."""
    entities = e9_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]

    for translation_file in translation_files:
        translations = json.loads(translation_file.read_text(encoding="utf-8"))[
            "entity"
        ]
        for config in entities.values():
            platform = cast("Platform", config["type"]).value
            translation_key = cast("str", config["translation_key"])
            name = translations[platform][translation_key]["name"].strip()
            assert name
            if translation_file.stem != "en":
                assert name != english[platform][translation_key]["name"]

        response_states = translations[Platform.SENSOR]["response_type"]["state"]
        for response in e9_message.RESPONSE_NAMES.values():
            state = response_states[response].strip()
            assert state
            if translation_file.stem != "en":
                assert (
                    state
                    != english[Platform.SENSOR]["response_type"]["state"][response]
                )
