"""Tests for the EB device registry mapping."""

import json
from pathlib import Path
from typing import cast

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.eb import DeviceAttributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def test_eb_registry_matches_library_attributes() -> None:
    """Expose all user-facing EB attributes on their matching HA platforms."""
    entities = cast(
        "dict[DeviceAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.EB]["entities"],
    )

    assert set(entities) == set(DeviceAttributes) - {DeviceAttributes.response}
    for attribute, config in entities.items():
        assert config["translation_key"] == attribute.value

    expected_platforms = {
        Platform.NUMBER: {
            DeviceAttributes.function_no,
            DeviceAttributes.work_status,
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


def test_eb_translations_cover_every_locale() -> None:
    """Require a localized name for every EB entity in every shipped locale."""
    entities = cast(
        "dict[DeviceAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.EB]["entities"],
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
