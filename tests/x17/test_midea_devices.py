"""Tests for the x17 clothes-drying rack registry entry."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import call

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.x17 import DeviceAttributes as X17Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.select import MideaSelect
from custom_components.midea_ac_lan.sensor import MideaSensor
from custom_components.midea_ac_lan.switch import MideaSwitch
from tests.helpers import DeviceFactory

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)
REPOSITORY_ROOT = Path(__file__).parents[2]
MOVEMENT_OPTIONS = ["pause", "up", "down"]
SWITCH_ATTRIBUTES = {
    X17Attributes.power,
    X17Attributes.light,
    X17Attributes.sterilize,
    X17Attributes.dry,
    X17Attributes.baking,
    X17Attributes.anion,
}


def x17_entities() -> dict[X17Attributes, dict[str, object]]:
    """Return the x17 entity registry with precise test typing."""
    return cast(
        "dict[X17Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.X17]["entities"],
    )


def test_registry_exposes_every_library_attribute() -> None:
    """Keep the integration synchronized with released x17 attributes."""
    entities = x17_entities()

    assert set(entities) == set(X17Attributes)
    assert {
        key for key, config in entities.items() if config["type"] == Platform.SWITCH
    } == SWITCH_ATTRIBUTES
    assert entities[X17Attributes.updown]["type"] == Platform.SELECT
    assert entities[X17Attributes.updown]["options"] == MOVEMENT_OPTIONS
    assert entities[X17Attributes.error_code]["type"] == Platform.SENSOR


def test_switches_read_reports_and_send_boolean_commands(
    device_factory: DeviceFactory,
) -> None:
    """Read every switch report and send both commands through the library API."""
    device, values = device_factory(
        device_type=DeviceType.X17,
        attributes=dict.fromkeys(SWITCH_ATTRIBUTES, False),
    )

    for attribute in SWITCH_ATTRIBUTES:
        entity = MideaSwitch(device, attribute)
        assert not entity.is_on
        values[attribute] = True
        assert entity.is_on
        entity.turn_off()
        entity.turn_on()

    assert device.set_attribute.call_args_list == [
        command
        for attribute in SWITCH_ATTRIBUTES
        for command in (
            call(attr=attribute, value=False),
            call(attr=attribute, value=True),
        )
    ]


def test_movement_select_reads_and_sends_every_library_option(
    device_factory: DeviceFactory,
) -> None:
    """Round-trip all movement states supported by the x17 library."""
    device, values = device_factory(
        device_type=DeviceType.X17,
        attributes={X17Attributes.updown: "pause"},
    )
    entity = MideaSelect(device, X17Attributes.updown)

    assert entity.options == MOVEMENT_OPTIONS
    for option in MOVEMENT_OPTIONS:
        values[X17Attributes.updown] = option
        assert entity.current_option == option
        entity.select_option(option)

    assert device.set_attribute.call_args_list == [
        call(X17Attributes.updown, option) for option in MOVEMENT_OPTIONS
    ]


def test_error_code_sensor_reads_library_attribute(
    device_factory: DeviceFactory,
) -> None:
    """Expose the library error code unchanged as a diagnostic sensor."""
    device, values = device_factory(
        device_type=DeviceType.X17,
        attributes={X17Attributes.error_code: 0},
    )
    entity = MideaSensor(device, X17Attributes.error_code)

    assert entity.native_value == 0
    values[X17Attributes.error_code] = 17
    assert entity.native_value == 17


def test_x17_translations_are_localized_in_every_locale() -> None:
    """Require every locale to translate all x17-specific UI text."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files

    localized: dict[str, tuple[str, ...]] = {}
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        updown = translation["entity"][Platform.SELECT]["updown"]
        entity_names = tuple(
            translation["entity"][config["type"]][config["translation_key"]]["name"]
            for config in x17_entities().values()
        )
        labels = (
            *entity_names,
            *(updown["state"][option] for option in MOVEMENT_OPTIONS),
        )
        assert all(isinstance(label, str) and label.strip() for label in labels)
        localized[translation_file.stem] = labels

    english_labels = localized.pop("en")
    assert all(labels != english_labels for labels in localized.values())


def test_x17_is_listed_in_every_readme_language() -> None:
    """Keep x17 visible in every supported-appliance index."""
    expected_rows = {
        "README.md": "| 17   | Clothes Drying Rack",
        "README_hans.md": "| 17   | 电动晾衣机",
        "README_hant.md": "| 17   | 電動曬衣架",
    }

    for readme, expected_row in expected_rows.items():
        content = (REPOSITORY_ROOT / readme).read_text(encoding="utf-8")
        assert expected_row in content
