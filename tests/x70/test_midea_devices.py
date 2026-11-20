"""Tests for the 0x70 seasoning dispenser registry mapping."""

import json
from pathlib import Path
from typing import Any, cast

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import Platform
from midealan.const import DeviceType
from midealan.devices.x70 import DeviceAttributes

from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.sensor import MideaSensor
from tests.helpers import DeviceFactory

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)
REPOSITORY_ROOT = Path(__file__).parents[2]


def x70_entities() -> dict[DeviceAttributes, dict[str, Any]]:
    """Return the 0x70 entity registry with precise test typing."""
    return cast(
        "dict[DeviceAttributes, dict[str, Any]]",
        MIDEA_DEVICES[DeviceType.X70]["entities"],
    )


def test_x70_registry_exposes_useful_released_attributes() -> None:
    """Expose each released box type and presence status as a sensor."""
    entities = x70_entities()
    expected_attributes = {
        getattr(DeviceAttributes, f"box{slot}_{field}")
        for slot in range(1, 9)
        for field in ("type", "status")
    }

    assert set(entities) == expected_attributes
    assert expected_attributes < set(DeviceAttributes)
    for attribute, config in entities.items():
        assert config["type"] is Platform.SENSOR
        assert config["translation_key"] == attribute.value
        assert config["entity_category"].value == "diagnostic"
        if attribute.value.endswith("_status"):
            assert config["device_class"] is SensorDeviceClass.ENUM
            assert config["options"] == {"no": "no", "missing": "missing"}


def test_x70_sensors_read_released_library_attributes(
    device_factory: DeviceFactory,
) -> None:
    """Read box type and map both presence states through generic sensors."""
    device, values = device_factory(
        device_type=DeviceType.X70,
        attributes={
            DeviceAttributes("box1_type"): 42,
            DeviceAttributes("box1_status"): "no",
        },
    )
    type_sensor = MideaSensor(device, DeviceAttributes("box1_type"))
    status_sensor = MideaSensor(device, DeviceAttributes("box1_status"))

    assert type_sensor.native_value == 42
    assert status_sensor.native_value == "no"
    assert status_sensor.options == ["no", "missing"]
    values[DeviceAttributes("box1_status")] = "missing"
    assert status_sensor.native_value == "missing"


def test_x70_translations_cover_every_locale_and_state() -> None:
    """Prevent every 0x70 sensor and state from falling back to English."""
    entities = x70_entities()
    translation_files = sorted(TRANSLATIONS_DIR.glob("*.json"))
    assert translation_files
    english = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"][Platform.SENSOR]

    for translation_file in translation_files:
        sensors = json.loads(translation_file.read_text(encoding="utf-8"))["entity"][
            Platform.SENSOR
        ]
        for config in entities.values():
            translation_key = cast("str", config["translation_key"])
            translation = sensors[translation_key]
            assert translation["name"].strip()
            if translation_file.stem != "en":
                assert translation["name"] != english[translation_key]["name"]
            for option in config.get("options", {}):
                state = translation["state"][option]
                assert state.strip()
                if translation_file.stem != "en":
                    assert state != english[translation_key]["state"][option]


def test_x70_is_listed_in_every_readme_language() -> None:
    """Keep 0x70 visible in every supported-appliance index."""
    expected_rows = {
        "README.md": "| 70   | Seasoning Dispenser",
        "README_hans.md": "| 70   | 调味机",
        "README_hant.md": "| 70   | 調味機",
    }

    for readme, expected_row in expected_rows.items():
        content = (REPOSITORY_ROOT / readme).read_text(encoding="utf-8")
        assert expected_row in content
