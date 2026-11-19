"""Tests for A1 group-one telemetry entities."""

import json
from pathlib import Path
from typing import cast

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfTemperature
from midealan.const import DeviceType
from midealan.devices.a1 import DeviceAttributes as A1Attributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def test_group_one_telemetry_entities() -> None:
    """Expose optional A1 group-one telemetry with capability guards."""
    entities = cast(
        "dict[A1Attributes, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.A1]["entities"],
    )

    assert entities[A1Attributes.compressor] == {
        "type": Platform.BINARY_SENSOR,
        "required_attribute": A1Attributes.compressor,
        "translation_key": "compressor",
        "name": "Compressor Running",
        "device_class": BinarySensorDeviceClass.RUNNING,
    }
    assert entities[A1Attributes.evaporator_temperature] == {
        "type": Platform.SENSOR,
        "required_attribute": A1Attributes.evaporator_temperature,
        "translation_key": "evaporator_temperature",
        "name": "Evaporator Temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "state_class": SensorStateClass.MEASUREMENT,
    }


def test_group_one_telemetry_names_exist_in_all_translations() -> None:
    """Require localized A1 telemetry names in every shipped language."""
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    for translation_file in translation_files:
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        assert translation["entity"]["binary_sensor"]["compressor"]["name"]
        assert translation["entity"]["sensor"]["evaporator_temperature"]["name"]
