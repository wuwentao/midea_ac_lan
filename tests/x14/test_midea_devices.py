"""Tests for the x14 electric-curtain registry entry."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import call

from homeassistant.const import PERCENTAGE, Platform
from midealan.const import DeviceType
from midealan.devices.x14 import DeviceAttributes as X14Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.number import MideaNumber
from custom_components.midea_ac_lan.select import MideaSelect
from custom_components.midea_ac_lan.sensor import MideaSensor
from tests.helpers import DeviceFactory

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)
REPOSITORY_ROOT = Path(__file__).parents[2]
STATUS_OPTIONS = ["open", "close", "stop"]
DIRECTION_OPTIONS = ["positive", "reverse"]


def x14_entities() -> dict[X14Attributes, dict[str, object]]:
    """Return the x14 entity registry with precise test typing."""
    return cast(
        "dict[X14Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.X14]["entities"],
    )


def test_registry_exposes_every_library_attribute() -> None:
    """Keep the integration synchronized with released x14 attributes."""
    entities = x14_entities()

    assert set(entities) == set(X14Attributes)
    assert entities[X14Attributes.curtain_status]["type"] == Platform.SELECT
    assert entities[X14Attributes.curtain_status]["options"] == STATUS_OPTIONS
    assert entities[X14Attributes.curtain_direction]["type"] == Platform.SELECT
    assert entities[X14Attributes.curtain_direction]["options"] == DIRECTION_OPTIONS
    assert entities[X14Attributes.curtain_position] == {
        "type": Platform.NUMBER,
        "translation_key": "curtain_position",
        "name": "Position",
        "icon": "mdi:percent",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": PERCENTAGE,
    }
    assert {
        attribute
        for attribute, config in entities.items()
        if config["type"] == Platform.SENSOR
    } == {X14Attributes.software_version, X14Attributes.error_code}


def test_selects_read_and_send_every_library_option(
    device_factory: DeviceFactory,
) -> None:
    """Round-trip every curtain status and direction supported by the library."""
    device, values = device_factory(
        device_type=DeviceType.X14,
        attributes={
            X14Attributes.curtain_status: STATUS_OPTIONS[0],
            X14Attributes.curtain_direction: DIRECTION_OPTIONS[0],
        },
    )
    status = MideaSelect(device, X14Attributes.curtain_status)
    direction = MideaSelect(device, X14Attributes.curtain_direction)

    assert status.options == STATUS_OPTIONS
    assert direction.options == DIRECTION_OPTIONS
    for entity, attribute, options in (
        (status, X14Attributes.curtain_status, STATUS_OPTIONS),
        (direction, X14Attributes.curtain_direction, DIRECTION_OPTIONS),
    ):
        for option in options:
            values[attribute] = option
            assert entity.current_option == option
            entity.select_option(option)

    assert device.set_attribute.call_args_list == [
        call(X14Attributes.curtain_status, option) for option in STATUS_OPTIONS
    ] + [call(X14Attributes.curtain_direction, option) for option in DIRECTION_OPTIONS]


def test_position_number_reads_and_sends_boundaries(
    device_factory: DeviceFactory,
) -> None:
    """Expose the library's complete 0-100 curtain-position range."""
    device, values = device_factory(
        device_type=DeviceType.X14,
        attributes={X14Attributes.curtain_position: 0},
    )
    entity = MideaNumber(device, X14Attributes.curtain_position)

    assert entity.native_min_value == 0
    assert entity.native_max_value == 100
    assert entity.native_step == 1
    assert entity.native_unit_of_measurement == PERCENTAGE
    for position in (0, 50, 100):
        values[X14Attributes.curtain_position] = position
        assert entity.native_value == position
        entity.set_native_value(position)

    assert device.set_attribute.call_args_list == [
        call(X14Attributes.curtain_position, position) for position in (0, 50, 100)
    ]


def test_diagnostic_sensors_read_library_attributes(
    device_factory: DeviceFactory,
) -> None:
    """Expose software version and error code reports unchanged."""
    device, values = device_factory(
        device_type=DeviceType.X14,
        attributes={
            X14Attributes.software_version: 16,
            X14Attributes.error_code: 0,
        },
    )
    software_version = MideaSensor(device, X14Attributes.software_version)
    error_code = MideaSensor(device, X14Attributes.error_code)

    assert software_version.native_value == 16
    assert error_code.native_value == 0
    values[X14Attributes.software_version] = 17
    values[X14Attributes.error_code] = 5
    assert software_version.native_value == 17
    assert error_code.native_value == 5


def test_x14_translations_are_localized_in_every_locale() -> None:
    """Require every locale to translate all x14-specific UI text."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files

    localized: dict[str, tuple[str, ...]] = {}
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        status = translation["entity"][Platform.SELECT]["curtain_status"]
        direction = translation["entity"][Platform.SELECT]["curtain_direction"]
        labels = (
            status["name"],
            *(status["state"][option] for option in STATUS_OPTIONS),
            direction["name"],
            *(direction["state"][option] for option in DIRECTION_OPTIONS),
            translation["entity"][Platform.NUMBER]["curtain_position"]["name"],
            translation["entity"][Platform.SENSOR]["software_version"]["name"],
            translation["entity"][Platform.SENSOR]["error_code"]["name"],
        )
        assert all(isinstance(label, str) and label.strip() for label in labels)
        localized[translation_file.stem] = labels

    english_labels = localized.pop("en")
    assert all(labels != english_labels for labels in localized.values())


def test_x14_is_listed_in_every_readme_language() -> None:
    """Keep x14 visible in every supported-appliance index."""
    expected_rows = {
        "README.md": "| 14   | Electric Curtain",
        "README_hans.md": "| 14   | 电动窗帘",
        "README_hant.md": "| 14   | 電動窗簾",
    }

    for readme, expected_row in expected_rows.items():
        content = (REPOSITORY_ROOT / readme).read_text(encoding="utf-8")
        assert expected_row in content
