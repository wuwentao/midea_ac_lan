"""Regression tests for the read-only 310A2111 flex-zone mode."""

# This suite uses unittest so no additional test dependency is needed.
# ruff: file-ignore[pytest-unittest-assertion, module-import-not-at-top-of-file, implicit-namespace-package]

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock, patch

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from midealan.device import MideaDevice

CUSTOM_COMPONENTS_ROOT = Path(__file__).parents[1] / "custom_components"
sys.path.insert(0, str(CUSTOM_COMPONENTS_ROOT))

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS
from midea_ac_lan.const import DEVICES, DOMAIN
from midea_ac_lan.sensor import MideaSensor, async_setup_entry
from midealan.devices.ca import DeviceAttributes as CAAttributes


class FakeRefrigeratorDevice:
    """Provide the public device properties consumed by sensor setup."""

    device_type = 0xCA
    device_id = 456
    name = "Test Refrigerator"
    model = "310A2111"
    subtype = 56
    mac = None
    serial_number = None
    available = True

    def __init__(self, mode: str | None = "treasure") -> None:
        """Store canonical values supplied by the library."""
        self.mode = mode
        self.attributes = {
            CAAttributes.variable_mode: mode,
            CAAttributes.flex_zone_setting_temp: 2,
        }

    def get_attribute(self, attribute: object) -> object:
        """Return the library's canonical mode or setting temperature.

        Returns
        -------
        The canonical mode, setting temperature, or missing value.

        """
        if attribute == CAAttributes.flex_zone_setting_temp:
            return 2
        if attribute == CAAttributes.variable_mode:
            return self.mode
        return None


def mode_sensor(device: FakeRefrigeratorDevice) -> MideaSensor:
    """Construct the generic entity using the public device contract.

    Returns
    -------
    The read-only mode sensor.

    """
    return MideaSensor(
        cast("MideaDevice", device),
        CAAttributes.variable_mode,
    )


class RefrigeratorFlexZoneModeTests(unittest.IsolatedAsyncioTestCase):
    """Cover interpretation, setup gates, translations, and push updates."""

    def test_verified_presets(self) -> None:
        """HA presents canonical library keys without temperature mapping."""
        device = FakeRefrigeratorDevice()
        entity = mode_sensor(device)
        for mode in entity.options or []:
            with self.subTest(mode=mode):
                device.mode = mode
                self.assertEqual(entity.native_value, mode)
        self.assertEqual(entity.device_class, SensorDeviceClass.ENUM)
        self.assertTrue(
            {"baby", "treasure", "zero", "none"}.issubset(entity.options or []),
        )
        self.assertEqual(entity.capability_attributes, {"options": entity.options})
        self.assertEqual(entity.entity_id, "sensor.456_variable_mode")

    def test_unverified_values_remain_unknown(self) -> None:
        """A missing library mode stays unknown, not derived from temperature."""
        device = FakeRefrigeratorDevice()
        entity = mode_sensor(device)
        device.mode = None
        self.assertIsNone(entity.native_value)

    @staticmethod
    async def setup_sensors(
        device: FakeRefrigeratorDevice,
        selected: list[str],
    ) -> list[MideaSensor]:
        """Exercise the real setup entry with an isolated device double.

        Returns
        -------
        The entities created by sensor setup.

        """
        hass = SimpleNamespace(data={DOMAIN: {DEVICES: {device.device_id: device}}})
        entry = SimpleNamespace(
            data={CONF_DEVICE_ID: device.device_id},
            options={CONF_SENSORS: selected},
        )
        entities: list[MideaSensor] = []
        await async_setup_entry(
            cast("HomeAssistant", hass),
            cast("ConfigEntry", entry),
            cast("AddEntitiesCallback", entities.extend),
        )
        return entities

    async def test_setup_gates_exact_model_and_subtype(self) -> None:
        """All opted-in devices use the same generic sensor class."""
        for model, subtype in (
            ("310A2111", 56),
            ("other", 56),
            ("310A2111", 1),
        ):
            with self.subTest(model=model, subtype=subtype):
                device = FakeRefrigeratorDevice()
                device.model = model
                device.subtype = subtype
                entities = await self.setup_sensors(
                    device,
                    [CAAttributes.variable_mode],
                )
                self.assertEqual(len(entities), 1)
                self.assertIs(type(entities[0]), MideaSensor)
                self.assertEqual(entities[0].native_value, "treasure")
        self.assertEqual(await self.setup_sensors(FakeRefrigeratorDevice(), []), [])

    async def test_other_attributes_keep_generic_sensor(self) -> None:
        """The exact target's temperature sensor keeps its existing behavior."""
        entities = await self.setup_sensors(
            FakeRefrigeratorDevice(),
            [CAAttributes.flex_zone_setting_temp],
        )
        self.assertEqual(len(entities), 1)
        self.assertIs(type(entities[0]), MideaSensor)
        self.assertEqual(entities[0].native_value, 2)

    def test_source_temperature_push_updates_mode(self) -> None:
        """Source updates reach HA once and do not mutate the status payload."""
        entity = mode_sensor(FakeRefrigeratorDevice())
        entity.hass = cast("HomeAssistant", Mock())
        for status in (
            {
                CAAttributes.flex_zone_setting_temp: 6,
                CAAttributes.variable_mode: "baby",
            },
            {
                CAAttributes.flex_zone_setting_temp: 2,
                CAAttributes.variable_mode: "none",
            },
            {"available": False},
            {CAAttributes.variable_mode: "none"},
        ):
            with self.subTest(status=status):
                original = status.copy()
                with patch.object(entity, "schedule_update_if_running") as schedule:
                    entity.update_state(status)
                    schedule.assert_called_once_with()
                self.assertEqual(status, original)
        with patch.object(entity, "schedule_update_if_running") as schedule:
            entity.update_state({CAAttributes.freezer_setting_temp: -18})
            schedule.assert_not_called()

    def test_english_and_chinese_enum_labels(self) -> None:
        """Every emitted mode has an English and Simplified Chinese label."""
        translations = CUSTOM_COMPONENTS_ROOT / "midea_ac_lan" / "translations"
        for filename, expected in (
            (
                "en.json",
                {
                    "baby": "Mother & Infant",
                    "treasure": "Treasure",
                    "zero": "Zero Degree",
                },
            ),
            ("zh-Hans.json", {"baby": "母婴", "treasure": "珍品", "zero": "零度"}),
        ):
            with self.subTest(filename=filename):
                document = json.loads(
                    (translations / filename).read_text(encoding="utf-8"),
                )
                self.assertEqual(
                    {
                        key: document["entity"]["sensor"]["variable_mode"]["state"][key]
                        for key in expected
                    },
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
