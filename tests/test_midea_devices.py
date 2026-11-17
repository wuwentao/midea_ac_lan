"""Tests for version-dependent device registry constants."""

from types import SimpleNamespace
from typing import cast

import homeassistant.const as ha_const
import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    MAJOR_VERSION,
    MINOR_VERSION,
    Platform,
    UnitOfTemperature,
)

from custom_components.midea_ac_lan.midea_devices import (
    A1_COMPRESSOR,
    A1_EVAPORATOR_TEMPERATURE,
    MIDEA_DEVICES,
)

from .helpers import load_integration_module


def test_a1_group_one_telemetry_entities() -> None:
    """Expose optional A1 group-one telemetry with capability guards."""
    entities = cast("dict[str, dict[str, object]]", MIDEA_DEVICES[0xA1]["entities"])

    assert entities[A1_COMPRESSOR] == {
        "type": Platform.BINARY_SENSOR,
        "required_attribute": A1_COMPRESSOR,
        "translation_key": "compressor_on",
        "name": "Compressor Running",
        "device_class": BinarySensorDeviceClass.RUNNING,
    }
    assert entities[A1_EVAPORATOR_TEMPERATURE] == {
        "type": Platform.SENSOR,
        "required_attribute": A1_EVAPORATOR_TEMPERATURE,
        "translation_key": "evaporator_temperature",
        "name": "Evaporator Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    }


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
