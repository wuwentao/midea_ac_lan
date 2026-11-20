"""Tests for the x10 power appliance registry entry."""

import json
from pathlib import Path
from typing import cast
from unittest.mock import call

from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.x10 import DeviceAttributes as X10Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.switch import MideaSwitch
from tests.helpers import DeviceFactory

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)
REPOSITORY_ROOT = Path(__file__).parents[2]


def x10_entities() -> dict[X10Attributes, dict[str, object]]:
    """Return the x10 entity registry with precise test typing."""
    return cast(
        "dict[X10Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.X10]["entities"],
    )


def test_registry_exposes_every_library_attribute() -> None:
    """Keep the integration synchronized with the released x10 attributes."""
    entities = x10_entities()

    assert set(entities) == set(X10Attributes)
    assert entities[X10Attributes.power] == {
        "type": Platform.SWITCH,
        "translation_key": "power",
        "name": "Power",
        "icon": "mdi:power",
        "default": True,
    }


def test_power_switch_reads_and_writes_library_attribute(
    device_factory: DeviceFactory,
) -> None:
    """Read power reports and send both supported switch commands."""
    device, values = device_factory(
        device_type=DeviceType.X10,
        attributes={X10Attributes.power: False},
    )
    entity = MideaSwitch(device, X10Attributes.power)

    assert entity._attr_translation_key == "power"
    assert not entity.is_on
    values[X10Attributes.power] = True
    assert entity.is_on

    entity.turn_off()
    entity.turn_on()
    assert device.set_attribute.call_args_list == [
        call(attr=X10Attributes.power, value=False),
        call(attr=X10Attributes.power, value=True),
    ]


def test_power_translation_is_localized_in_every_locale() -> None:
    """Require every shipped locale to name x10 power without English fallback."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    assert any(translation_file.stem == "en" for translation_file in translation_files)

    names: dict[str, str] = {}
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        name = translation["entity"][Platform.SWITCH]["power"]["name"]
        assert isinstance(name, str)
        assert name.strip()
        names[translation_file.stem] = name

    english_name = names.pop("en")
    assert all(name != english_name for name in names.values())


def test_x10_is_listed_in_every_readme_language() -> None:
    """Keep x10 visible in every supported-appliance index."""
    expected_rows = {
        "README.md": "| 10   | Power Appliance",
        "README_hans.md": "| 10   | 电源电器",
        "README_hant.md": "| 10   | 電源電器",
    }

    for readme, expected_row in expected_rows.items():
        content = (REPOSITORY_ROOT / readme).read_text(encoding="utf-8")
        assert expected_row in content
