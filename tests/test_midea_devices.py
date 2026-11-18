"""Tests for version-dependent device registry constants."""

import json
from pathlib import Path
from types import SimpleNamespace

import homeassistant.const as ha_const
import pytest
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION

from .helpers import load_integration_module

TRANSLATIONS_DIR = (
    Path(__file__).parent.parent / "custom_components" / "midea_ac_lan" / "translations"
)


def test_x13_entity_names_exist_in_all_translations() -> None:
    """Require localized X13 fan and light names in every shipped language."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        assert translation["entity"]["fan"]["fan"]["name"]
        assert translation["entity"]["light"]["light"]["name"]


def test_opposite_version_concentration_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Execute the concentration-unit branch opposite to the installed HA."""
    installed_has_unit_enums = (MAJOR_VERSION, MINOR_VERSION) >= (2026, 7)
    target_version = (2026, 6) if installed_has_unit_enums else (2026, 7)
    monkeypatch.setattr(ha_const, "MAJOR_VERSION", target_version[0])
    monkeypatch.setattr(ha_const, "MINOR_VERSION", target_version[1])

    if target_version >= (2026, 7):
        monkeypatch.setattr(
            ha_const,
            "UnitOfDensity",
            SimpleNamespace(MICROGRAMS_PER_CUBIC_METER="μg/m³"),
            raising=False,
        )
        monkeypatch.setattr(
            ha_const,
            "UnitOfRatio",
            SimpleNamespace(PARTS_PER_MILLION="ppm"),
            raising=False,
        )
    else:
        monkeypatch.setattr(
            ha_const,
            "CONCENTRATION_MICROGRAMS_PER_CUBIC_METER",
            "μg/m³",
            raising=False,
        )
        monkeypatch.setattr(
            ha_const,
            "CONCENTRATION_PARTS_PER_MILLION",
            "ppm",
            raising=False,
        )

    module = load_integration_module(
        "midea_devices",
        f"midea_devices_{target_version[1]}",
    )

    assert module.CONCENTRATION_MICROGRAMS_PER_CUBIC_METER == "μg/m³"
    assert module.CONCENTRATION_PARTS_PER_MILLION == "ppm"
