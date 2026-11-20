"""Tests for the 0xB2 device registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.const import Platform, UnitOfTemperature, UnitOfTime
from midealan.const import DeviceType
from midealan.devices.b2 import DeviceAttributes
from midealan.devices.b2.message import (
    BOX_STATE_NAMES,
    DOOR_STATE_NAMES,
    MODE_CODES,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    WATER_STATE_NAMES,
    WORK_HOUR_MAX,
    WORK_HOUR_MIN,
    WORK_MINUTE_MAX,
    WORK_MINUTE_MIN,
    WORK_STATUS_CODES,
    WORK_STATUS_NAMES,
)

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def b2_entities() -> dict[DeviceAttributes | str, dict[str, Any]]:
    """Return the 0xB2 registry mapping with precise test typing."""
    return cast(
        "dict[DeviceAttributes | str, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.B2]["entities"],
    )


def test_b2_registry_matches_released_library() -> None:
    """Keep every 0xB2 entity aligned with the released library API."""
    entities = b2_entities()

    assert set(entities) == {*DeviceAttributes, "work_status_select"}
    assert entities[DeviceAttributes.work_status]["type"] is Platform.SENSOR
    assert entities["work_status_select"]["type"] is Platform.SELECT
    assert entities["work_status_select"]["attribute"] is DeviceAttributes.work_status
    assert entities["work_status_select"]["options"] == list(WORK_STATUS_CODES)
    assert entities[DeviceAttributes.work_mode]["options"] == list(MODE_CODES)
    assert set(WORK_STATUS_NAMES.values()) - set(WORK_STATUS_CODES) == {
        "work_finish",
    }

    expected_options = {
        DeviceAttributes.work_status: set(WORK_STATUS_NAMES.values()),
        DeviceAttributes.door_state: set(DOOR_STATE_NAMES.values()),
        DeviceAttributes.water_state: set(WATER_STATE_NAMES.values()),
        DeviceAttributes.box_state: set(BOX_STATE_NAMES.values()),
    }
    for attribute, states in expected_options.items():
        assert entities[attribute]["options"] == {state: state for state in states}


def test_b2_number_controls_match_library_ranges() -> None:
    """Keep HA number limits and units synchronized with midea-lan 2026.11.0."""
    entities = b2_entities()
    expected = {
        DeviceAttributes.work_hour: (
            WORK_HOUR_MIN,
            WORK_HOUR_MAX,
            UnitOfTime.HOURS,
        ),
        DeviceAttributes.work_minute: (
            WORK_MINUTE_MIN,
            WORK_MINUTE_MAX,
            UnitOfTime.MINUTES,
        ),
        DeviceAttributes.temperature: (
            TEMPERATURE_MIN,
            TEMPERATURE_MAX,
            UnitOfTemperature.CELSIUS,
        ),
    }

    for attribute, (minimum, maximum, unit) in expected.items():
        config = entities[attribute]
        assert config["min"] == minimum
        assert config["max"] == maximum
        assert config["unit"] == unit
        assert config["step"] == 1


def test_b2_translation_keys_follow_shared_key_rules() -> None:
    """Reuse matching shared keys and use attribute names for new keys."""
    entities = b2_entities()
    expected_keys = {
        DeviceAttributes.work_status: "work_status",
        DeviceAttributes.work_mode: "mode",
        DeviceAttributes.work_hour: "hour_set",
        DeviceAttributes.work_minute: "minute_set",
        DeviceAttributes.temperature: "temperature_number",
        DeviceAttributes.door_state: "door_state",
        DeviceAttributes.water_state: "water_state",
        DeviceAttributes.box_state: "box_state",
        DeviceAttributes.lock: "lock",
    }

    for attribute, translation_key in expected_keys.items():
        assert entities[attribute]["translation_key"] == translation_key
    assert entities["work_status_select"]["translation_key"] == "work_status_select"


def test_b2_translations_cover_every_locale_and_state() -> None:
    """Prevent any 0xB2 entity or state from falling back to English."""
    entities = b2_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]
    language_invariant_text = {
        ("ca", Platform.SELECT.value, "mode", "name"),
        ("ca", Platform.SELECT.value, "mode", "common"),
        ("de", Platform.SELECT.value, "work_status_select", "standby"),
        ("de", Platform.SENSOR.value, "work_status", "standby"),
        ("es", Platform.SELECT.value, "mode", "common"),
        ("fr", Platform.SELECT.value, "mode", "name"),
        ("fr", Platform.SELECT.value, "mode", "zymosis"),
        ("it", Platform.SELECT.value, "work_status_select", "standby"),
        ("it", Platform.SENSOR.value, "work_status", "standby"),
        ("nb", Platform.SELECT.value, "mode", "egg"),
        ("nb", Platform.SENSOR.value, "water_state", "full"),
        ("nl", Platform.SENSOR.value, "door_state", "open"),
        ("ro", Platform.SELECT.value, "mode", "common"),
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
                        "name",
                    )
                    in language_invariant_text
                )
            for option in config.get("options", []):
                state = translation["state"][option].strip()
                assert state
                if translation_file.stem != "en":
                    uses_english_state = (
                        state == english[platform][translation_key]["state"][option]
                    )
                    assert (
                        not uses_english_state
                        or (
                            translation_file.stem,
                            platform,
                            translation_key,
                            option,
                        )
                        in language_invariant_text
                    )

        reported_states = translations[Platform.SENSOR]["work_status"]["state"]
        for status in WORK_STATUS_NAMES.values():
            state = reported_states[status].strip()
            assert state
            if translation_file.stem != "en":
                uses_english_state = (
                    state == english[Platform.SENSOR]["work_status"]["state"][status]
                )
                assert (
                    not uses_english_state
                    or (
                        translation_file.stem,
                        Platform.SENSOR.value,
                        "work_status",
                        status,
                    )
                    in language_invariant_text
                )
