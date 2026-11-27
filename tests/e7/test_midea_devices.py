"""Tests for the E7 device registry mapping."""

import json
from pathlib import Path
from typing import cast

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.e7 import DeviceAttributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def test_e7_registry_matches_library_attributes() -> None:
    """Expose all user-facing E7 attributes on their matching HA platforms."""
    entities = cast(
        "dict[DeviceAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.E7]["entities"],
    )

    assert set(entities) == set(DeviceAttributes) - {DeviceAttributes.response}
    for attribute, config in entities.items():
        assert config["translation_key"] == attribute.value

    expected_platforms = {
        Platform.NUMBER: {
            DeviceAttributes.work_status,
            DeviceAttributes.function_num,
            DeviceAttributes.fire_level,
            DeviceAttributes.time_reserve_hr,
            DeviceAttributes.time_reserve_min,
            DeviceAttributes.definite_time_hr,
            DeviceAttributes.definite_time_min,
        },
        Platform.SENSOR: {
            DeviceAttributes.time_running_hr,
            DeviceAttributes.time_running_min,
            DeviceAttributes.time_surplus_hr,
            DeviceAttributes.time_surplus_min,
            DeviceAttributes.work_stage,
            DeviceAttributes.error_code,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes

    function_num = entities[DeviceAttributes.function_num]
    assert function_num["max"] == 0xFFFFFFFF
    assert function_num["max_by_subtype"] == {6: 0xFFFF}


def test_e7_translations_cover_every_locale() -> None:
    """Require a localized name for every E7 entity in every shipped locale."""
    entities = cast(
        "dict[DeviceAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.E7]["entities"],
    )
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files

    for translation_file in translation_files:
        translations = cast(
            "dict[str, dict[str, dict[str, dict[str, str]]]]",
            json.loads(translation_file.read_text(encoding="utf-8")),
        )["entity"]
        for config in entities.values():
            platform = cast("Platform", config["type"]).value
            translation_key = cast("str", config["translation_key"])
            assert translations[platform][translation_key]["name"]
