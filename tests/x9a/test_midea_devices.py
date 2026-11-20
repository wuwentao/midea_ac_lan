"""Tests for the 0x9A device registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from midealan.const import DeviceType
from midealan.devices.x9a import (
    HOUR_MAX,
    HOUR_MIN,
    MINUTE_MAX,
    MINUTE_MIN,
    SECOND_MAX,
    SECOND_MIN,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    WATT_MAX,
    WATT_MIN,
    WEIGHT_MAX,
    WEIGHT_MIN,
    DeviceAttributes,
)
from midealan.devices.x9a.message import (
    MODE_CODES,
    WORK_STATUS_CODES,
    WORK_STATUS_NAMES,
)

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def x9a_entities() -> dict[DeviceAttributes | str, dict[str, Any]]:
    """Return the 0x9A registry mapping with precise test typing."""
    return cast(
        "dict[DeviceAttributes | str, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.X9A]["entities"],
    )


def test_x9a_registry_matches_released_library() -> None:
    """Keep every 0x9A entity aligned with the released library API."""
    entities = x9a_entities()

    assert set(entities) == {*DeviceAttributes, "work_status_select"}
    assert {
        attribute
        for attribute, config in entities.items()
        if config["type"] is Platform.SWITCH
    } == {
        DeviceAttributes.power,
        DeviceAttributes.lock,
        DeviceAttributes.furnace_light,
    }
    assert {
        attribute
        for attribute, config in entities.items()
        if config["type"] is Platform.SELECT
    } == {DeviceAttributes.mode, "work_status_select"}
    assert {
        attribute
        for attribute, config in entities.items()
        if config["type"] is Platform.NUMBER
    } == {
        DeviceAttributes.temperature,
        DeviceAttributes.hour,
        DeviceAttributes.minutes,
        DeviceAttributes.second,
        DeviceAttributes.watt,
        DeviceAttributes.weight,
    }
    assert {
        attribute
        for attribute, config in entities.items()
        if config["type"] is Platform.SENSOR
    } == {
        DeviceAttributes.work_status,
        DeviceAttributes.current_temperature,
        DeviceAttributes.error_code,
    }

    assert entities["work_status_select"]["attribute"] is DeviceAttributes.work_status
    assert entities["work_status_select"]["options"] == list(WORK_STATUS_CODES)
    assert entities[DeviceAttributes.mode]["options"] == list(MODE_CODES)


def test_x9a_number_controls_match_library_ranges() -> None:
    """Keep HA number limits and units synchronized with midea-lan 2026.11.0."""
    entities = x9a_entities()
    expected = {
        DeviceAttributes.temperature: (
            TEMPERATURE_MIN,
            TEMPERATURE_MAX,
            UnitOfTemperature.CELSIUS,
        ),
        DeviceAttributes.hour: (HOUR_MIN, HOUR_MAX, UnitOfTime.HOURS),
        DeviceAttributes.minutes: (MINUTE_MIN, MINUTE_MAX, UnitOfTime.MINUTES),
        DeviceAttributes.second: (SECOND_MIN, SECOND_MAX, UnitOfTime.SECONDS),
        DeviceAttributes.watt: (WATT_MIN, WATT_MAX, None),
        DeviceAttributes.weight: (WEIGHT_MIN, WEIGHT_MAX, "g"),
    }

    for attribute, (minimum, maximum, unit) in expected.items():
        config = entities[attribute]
        assert config["min"] == minimum
        assert config["max"] == maximum
        if unit is None:
            assert "unit" not in config
        else:
            assert config["unit"] == unit

    assert entities[DeviceAttributes.weight]["step"] == 10
    for attribute in set(expected) - {DeviceAttributes.weight}:
        assert entities[attribute]["step"] == 1


def test_x9a_translation_keys_follow_shared_key_rules() -> None:
    """Reuse matching shared keys and use attribute names for new keys."""
    entities = x9a_entities()
    expected_keys = {
        DeviceAttributes.temperature: "temperature_number",
        DeviceAttributes.hour: "hour_set",
        DeviceAttributes.minutes: "minute_set",
        DeviceAttributes.second: "second_set",
    }

    for attribute in DeviceAttributes:
        expected_key = expected_keys.get(attribute, attribute.value)
        assert entities[attribute]["translation_key"] == expected_key
    assert entities["work_status_select"]["translation_key"] == "work_status_select"


def test_x9a_translations_cover_every_locale_and_state() -> None:
    """Prevent every 0x9A entity and state from falling back to English."""
    entities = x9a_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads((TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"))[
        "entity"
    ]
    language_invariant_names = {
        ("ca", Platform.SELECT.value, "mode"),
        ("fr", Platform.SELECT.value, "mode"),
    }

    for translation_file in translation_files:
        translations = json.loads(translation_file.read_text(encoding="utf-8"))[
            "entity"
        ]
        for config in entities.values():
            platform = cast("Platform", config["type"]).value
            translation_key = cast("str", config["translation_key"])
            translation = translations[platform][translation_key]
            name = translation["name"].strip()
            assert name
            if translation_file.stem != "en":
                uses_english_name = name == english[platform][translation_key]["name"]
                assert (
                    not uses_english_name
                    or (
                        translation_file.stem,
                        platform,
                        translation_key,
                    )
                    in language_invariant_names
                )
            for option in config.get("options", []):
                assert translation["state"][option].strip()

        reported_states = translations[Platform.SENSOR]["work_status"]["state"]
        for status in WORK_STATUS_NAMES.values():
            assert reported_states[status].strip()
