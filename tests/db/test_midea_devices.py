"""Tests for DB v41 device registry entries."""

import json
from pathlib import Path
from typing import cast

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfTime
from midealan.const import DeviceType
from midealan.devices.db import DeviceAttributes as DBAttributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)
SENSOR_ATTRIBUTES = {
    DBAttributes.dryer,
    DBAttributes.soak_count,
    DBAttributes.appointment_time,
    DBAttributes.error_code,
    DBAttributes.water_consumption,
    DBAttributes.power_consumption,
    DBAttributes.wash_count,
}
BINARY_SENSOR_ATTRIBUTES = {
    DBAttributes.speedy,
    DBAttributes.lock,
    DBAttributes.beforehand_wash,
    DBAttributes.steam_wash,
    DBAttributes.add_rinse,
    DBAttributes.wind_dispel,
    DBAttributes.remote_control_flag,
}
TRANSLATION_KEYS = {
    DBAttributes.water_consumption: "db_last_cycle_water_consumption",
}
OLD_TRANSLATION_KEYS = {
    "washer_dryer",
    "washer_soak_count",
    "washer_appointment_time",
    "washer_error_code",
    "washer_water_consumption",
    "washer_power_consumption",
    "washer_wash_count",
    "washer_speedy",
    "washer_child_lock",
    "washer_prewash",
    "washer_steam_wash",
    "washer_add_rinse",
    "washer_fresh_air",
    "washer_remote_control",
}
# Explicitly list unavoidable English-identical localized values as
# (locale, platform, translation key). Keep this narrow so one untranslated
# key cannot hide behind the other localized values in its locale.
ENGLISH_EQUIVALENT_TRANSLATIONS: set[tuple[str, str, str]] = set()


def db_entities() -> dict[DBAttributes, dict[str, object]]:
    """Return the DB entity registry with precise test typing."""
    return cast(
        "dict[DBAttributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.DB]["entities"],
    )


def test_v41_registry_uses_library_attributes_and_matching_translation_keys() -> None:
    """Keep v41 registry keys aligned with the released library enum."""
    entities = db_entities()

    for attribute in SENSOR_ATTRIBUTES:
        assert entities[attribute]["type"] is Platform.SENSOR
    for attribute in BINARY_SENSOR_ATTRIBUTES:
        assert entities[attribute]["type"] is Platform.BINARY_SENSOR

    for attribute in SENSOR_ATTRIBUTES | BINARY_SENSOR_ATTRIBUTES:
        expected_key = TRANSLATION_KEYS.get(attribute, attribute.value)
        assert entities[attribute]["translation_key"] == expected_key


def test_v41_required_attributes_and_sensor_metadata() -> None:
    """Retain v41 capability guards and Home Assistant sensor metadata."""
    entities = db_entities()
    cycle_end_attributes = {
        DBAttributes.water_consumption,
        DBAttributes.power_consumption,
        DBAttributes.wash_count,
    }

    for attribute in (
        SENSOR_ATTRIBUTES | BINARY_SENSOR_ATTRIBUTES
    ) - cycle_end_attributes:
        assert entities[attribute]["required_attribute"] is attribute
    for attribute in cycle_end_attributes:
        assert entities[attribute]["required_attribute"] is DBAttributes.dryer
        assert entities[attribute]["restore_last_value"] is True

    appointment = entities[DBAttributes.appointment_time]
    assert appointment["device_class"] is SensorDeviceClass.DURATION
    assert appointment["unit"] is UnitOfTime.MINUTES
    assert (
        entities[DBAttributes.wash_count]["state_class"]
        is SensorStateClass.TOTAL_INCREASING
    )


def test_v41_translations_are_complete_and_localized() -> None:
    """Require every locale to provide localized names for every v41 entity."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert len(translation_files) == 26

    expected_by_platform = {
        Platform.SENSOR.value: SENSOR_ATTRIBUTES,
        Platform.BINARY_SENSOR.value: BINARY_SENSOR_ATTRIBUTES,
    }
    names_by_language: dict[str, dict[tuple[str, str], str]] = {}

    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        translated_entities = translation["entity"]
        names: dict[tuple[str, str], str] = {}

        for platform, attributes in expected_by_platform.items():
            platform_translations = translated_entities[platform]
            assert OLD_TRANSLATION_KEYS.isdisjoint(platform_translations)
            for attribute in sorted(attributes, key=lambda item: item.value):
                translation_key = TRANSLATION_KEYS.get(attribute, attribute.value)
                name = platform_translations[translation_key]["name"]
                assert isinstance(name, str)
                assert name.strip()
                names[platform, translation_key] = name

        names_by_language[translation_file.stem] = names

    english_names = names_by_language.pop("en")
    for language, localized_names in names_by_language.items():
        for (platform, translation_key), name in localized_names.items():
            exemption = (language, platform, translation_key)
            assert (
                name != english_names[platform, translation_key]
                or exemption in ENGLISH_EQUIVALENT_TRANSLATIONS
            )

    for language, platform, translation_key in ENGLISH_EQUIVALENT_TRANSLATIONS:
        assert (
            names_by_language[language][platform, translation_key]
            == english_names[platform, translation_key]
        )
