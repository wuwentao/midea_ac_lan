"""Tests for the 0xEF device registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from midealan.const import DeviceType
from midealan.devices.ef import DeviceAttributes
from midealan.devices.ef import message as ef_message

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

REPOSITORY_ROOT = Path(__file__).parents[2]
TRANSLATIONS_DIR = (
    REPOSITORY_ROOT / "custom_components" / "midea_ac_lan" / "translations"
)


def ef_entities() -> dict[DeviceAttributes, dict[str, Any]]:
    """Return the 0xEF registry mapping with precise test typing."""
    return cast(
        "dict[DeviceAttributes, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.EF]["entities"],
    )


def test_ef_registry_matches_released_library() -> None:
    """Expose every attribute available in midea-lan 2026.11.0."""
    entities = ef_entities()

    assert set(entities) == set(DeviceAttributes)
    expected_platforms = {
        Platform.SWITCH: {
            DeviceAttributes.reserve,
            DeviceAttributes.warm,
        },
        Platform.SELECT: {DeviceAttributes.drink_style},
        Platform.NUMBER: {
            DeviceAttributes.cmd_code,
            DeviceAttributes.cmd_id,
            DeviceAttributes.time_reserve_hr,
            DeviceAttributes.time_reserve_min,
            DeviceAttributes.time_warm_hr,
            DeviceAttributes.time_warm_min,
            DeviceAttributes.temperature_setting,
        },
        Platform.SENSOR: {
            DeviceAttributes.work_status,
            DeviceAttributes.error_code,
            DeviceAttributes.response_type,
            DeviceAttributes.work_step,
            DeviceAttributes.process_status,
            DeviceAttributes.time_work_hr,
            DeviceAttributes.time_work_min,
            DeviceAttributes.time_max,
            DeviceAttributes.temperature_current,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes

    assert entities[DeviceAttributes.drink_style]["options"] == [
        ef_message.DRINK_HOT,
        ef_message.DRINK_WARM,
    ]
    response = entities[DeviceAttributes.response_type]
    assert response["device_class"] is SensorDeviceClass.ENUM
    assert response["options"] == {
        value: value for value in ef_message.RESPONSE_NAMES.values()
    }


def test_ef_number_controls_match_library_ranges() -> None:
    """Keep HA number limits synchronized with midea-lan 2026.11.0."""
    entities = ef_entities()
    expected = {
        DeviceAttributes.cmd_code: (
            ef_message.CMD_CODE_LOW,
            ef_message.CMD_CODE_HIGH,
            None,
        ),
        DeviceAttributes.cmd_id: (
            ef_message.CMD_ID_LOW,
            ef_message.CMD_ID_HIGH,
            None,
        ),
        DeviceAttributes.time_reserve_hr: (
            ef_message.TIME_HR_LOW,
            ef_message.TIME_HR_HIGH,
            UnitOfTime.HOURS,
        ),
        DeviceAttributes.time_reserve_min: (
            ef_message.TIME_MIN_LOW,
            ef_message.TIME_MIN_HIGH,
            UnitOfTime.MINUTES,
        ),
        DeviceAttributes.time_warm_hr: (
            ef_message.TIME_HR_LOW,
            ef_message.TIME_HR_HIGH,
            UnitOfTime.HOURS,
        ),
        DeviceAttributes.time_warm_min: (
            ef_message.TIME_MIN_LOW,
            ef_message.TIME_MIN_HIGH,
            UnitOfTime.MINUTES,
        ),
        DeviceAttributes.temperature_setting: (
            ef_message.TEMPERATURE_LOW,
            ef_message.TEMPERATURE_HIGH,
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
        entities[DeviceAttributes.temperature_setting]["device_class"]
        is NumberDeviceClass.TEMPERATURE
    )


def test_ef_sensor_metadata() -> None:
    """Expose EF temperature and duration telemetry with HA metadata."""
    entities = ef_entities()
    current_temperature = entities[DeviceAttributes.temperature_current]
    assert current_temperature["device_class"] is SensorDeviceClass.TEMPERATURE
    assert current_temperature["unit"] == UnitOfTemperature.CELSIUS
    assert current_temperature["state_class"] is SensorStateClass.MEASUREMENT

    durations = {
        DeviceAttributes.time_work_hr: UnitOfTime.HOURS,
        DeviceAttributes.time_work_min: UnitOfTime.MINUTES,
    }
    for attribute, unit in durations.items():
        config = entities[attribute]
        assert config["device_class"] is SensorDeviceClass.DURATION
        assert config["unit"] == unit
        assert config["state_class"] is SensorStateClass.MEASUREMENT


def test_ef_translation_keys_follow_shared_key_rules() -> None:
    """Reuse semantic keys and otherwise match the device attribute name."""
    overrides = {
        DeviceAttributes.warm: "keep_warm",
        DeviceAttributes.cmd_code: "control_cmd_code",
        DeviceAttributes.work_step: "step_status",
        DeviceAttributes.temperature_current: "current_temperature",
    }

    for attribute, config in ef_entities().items():
        assert config["translation_key"] == overrides.get(attribute, attribute.value)
        assert not cast("str", config["translation_key"]).startswith("ef_")


def test_ef_translations_cover_every_locale_without_english_fallback() -> None:
    """Require localized EF names and enum states in every shipped locale."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]
    new_translation_paths = (
        (Platform.SWITCH, "reserve", "name"),
        (Platform.NUMBER, "temperature_setting", "name"),
        (Platform.NUMBER, "time_warm_hr", "name"),
        (Platform.NUMBER, "time_warm_min", "name"),
        (Platform.NUMBER, "cmd_id", "name"),
        (Platform.SELECT, "drink_style", "name"),
        (Platform.SENSOR, "process_status", "name"),
        (Platform.SENSOR, "time_max", "name"),
    )
    english_new_values = [
        english[platform][key][field] for platform, key, field in new_translation_paths
    ]

    for translation_file in translation_files:
        translations = json.loads(translation_file.read_text(encoding="utf-8"))[
            "entity"
        ]
        for config in ef_entities().values():
            platform = cast("Platform", config["type"]).value
            translation_key = cast("str", config["translation_key"])
            assert translations[platform][translation_key]["name"].strip()

        drink_states = translations[Platform.SELECT]["drink_style"]["state"]
        assert all(
            drink_states[option].strip()
            for option in ef_entities()[DeviceAttributes.drink_style]["options"]
        )
        response_states = translations[Platform.SENSOR]["response_type"]["state"]
        assert all(
            response_states[option].strip()
            for option in ef_entities()[DeviceAttributes.response_type]["options"]
        )

        localized_new_values = [
            translations[platform][key][field]
            for platform, key, field in new_translation_paths
        ]
        if translation_file.stem != "en":
            assert localized_new_values != english_new_values


def test_ef_documentation_uses_real_entity_ids() -> None:
    """Document entity IDs from attribute keys without an EF-only prefix."""
    for document in ("doc/EF.md", "doc/EF_hans.md"):
        content = (REPOSITORY_ROOT / document).read_text(encoding="utf-8")
        assert "\\_ef_" not in content
        for attribute in DeviceAttributes:
            assert f"\\_{attribute.value}" in content

    expected_rows = {
        "README.md": "| EF   | Beverage Maker",
        "README_hans.md": "| EF   | 饮品机",
        "README_hant.md": "| EF   | 飲品機",
    }
    for readme, expected_row in expected_rows.items():
        content = (REPOSITORY_ROOT / readme).read_text(encoding="utf-8")
        assert expected_row in content
