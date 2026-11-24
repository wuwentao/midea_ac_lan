"""Tests for CA-specific device metadata."""

import json
from pathlib import Path
from typing import cast

from midealan.const import DeviceType

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def test_ca_mode_switch_translations_exist_in_all_locales() -> None:
    """Require localized names for every CA refrigerator mode switch."""
    entities = cast(
        "dict[str, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.CA]["entities"],
    )
    expected = {
        "refrigeracao_rapida": "storage_mode",
        "congelamento_rapido": "freezing_mode",
        "modo_ferias": "holiday_on",
    }
    for entity_key, translation_key in expected.items():
        assert entities[entity_key]["translation_key"] == translation_key
    for translation_file in TRANSLATIONS_DIR.glob("*.json"):
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        switches = translation["entity"]["switch"]
        for translation_key in expected.values():
            assert switches[translation_key]["name"]
