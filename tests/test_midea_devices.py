"""Tests for version-dependent device registry constants."""

from types import SimpleNamespace
from typing import Any, cast

import homeassistant.const as ha_const
import pytest
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION, Platform
from midealan.const import DeviceType
from midealan.devices.x44 import DeviceAttributes as X44Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

from .helpers import load_integration_module


def test_x44_registry_matches_library_attributes() -> None:
    """Keep every library x44 attribute exposed on the matching HA platform."""
    entities = cast(
        "dict[str, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.X44]["entities"],
    )

    assert set(entities) == set(X44Attributes)
    expected_platforms = {
        Platform.BINARY_SENSOR: {X44Attributes.has_token},
        Platform.SENSOR: {
            X44Attributes.panel_status,
            X44Attributes.error_code,
        },
        Platform.SWITCH: {
            X44Attributes.left_button,
            X44Attributes.middle_button,
            X44Attributes.right_button,
            X44Attributes.show_button_name,
            X44Attributes.close_screen_bright,
            X44Attributes.sleep_mode_switch,
            X44Attributes.sleep_mode_mute,
            X44Attributes.left_button_keep,
            X44Attributes.middle_button_keep,
            X44Attributes.right_button_keep,
            X44Attributes.voice_control,
            X44Attributes.sleep_mode,
            X44Attributes.screen_state,
        },
        Platform.NUMBER: {
            X44Attributes.auto_off_screen_type,
            X44Attributes.theme,
            X44Attributes.night_volume,
            X44Attributes.voice_volume,
            X44Attributes.sleep_start_hour,
            X44Attributes.sleep_start_minute,
            X44Attributes.sleep_duration_hour,
            X44Attributes.sleep_duration_minute,
            X44Attributes.brightness,
            X44Attributes.left_button_work_mode,
            X44Attributes.middle_button_work_mode,
            X44Attributes.right_button_work_mode,
        },
    }
    for platform, expected_attributes in expected_platforms.items():
        assert {
            attribute
            for attribute, config in entities.items()
            if config["type"] is platform
        } == expected_attributes

    byte_numbers = expected_platforms[Platform.NUMBER] - {
        X44Attributes.sleep_start_hour,
        X44Attributes.sleep_start_minute,
        X44Attributes.sleep_duration_minute,
    }
    for attribute in byte_numbers:
        assert (
            entities[attribute]["min"],
            entities[attribute]["max"],
            entities[attribute]["step"],
        ) == (0, 254, 1)
    for attribute, maximum in {
        X44Attributes.sleep_start_hour: 23,
        X44Attributes.sleep_start_minute: 59,
        X44Attributes.sleep_duration_minute: 59,
    }.items():
        assert (
            entities[attribute]["min"],
            entities[attribute]["max"],
            entities[attribute]["step"],
        ) == (0, maximum, 1)


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
