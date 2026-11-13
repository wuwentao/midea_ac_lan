"""Tests for Midea sensor entities."""

from datetime import date
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform
from midealan.devices.e1 import MideaE1Device

from custom_components.midea_ac_lan.const import supports_device
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.sensor import (
    MideaCloudUsageSensor,
    MideaEstimatedUsageSensor,
    MideaFlagStateSensor,
    MideaMinuteDurationSensor,
    MideaSensor,
    async_setup_entry,
)

from .helpers import (
    TEST_DEVICE_TYPE,
    DeviceFactory,
    InstallConfig,
    setup_context,
)


async def test_async_setup_entry_builds_all_sensor_types(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Build each specialized sensor and share one cloud coordinator."""
    install_config(
        {
            "cloud_one": {
                "type": Platform.SENSOR,
                "default": True,
                "cloud_report": "energy",
            },
            "cloud_two": {
                "type": Platform.SENSOR,
                "default": True,
                "cloud_report": "water",
            },
            "estimate": {
                "type": Platform.SENSOR,
                "default": True,
                "estimate": {"values_by_model": {}},
            },
            "duration": {
                "type": Platform.SENSOR,
                "default": True,
                "duration_from_minutes": True,
            },
            "flags": {
                "type": Platform.SENSOR,
                "default": True,
                "state_from_flags": {"working": "on"},
            },
            "plain": {"type": Platform.SENSOR},
            "missing": {
                "type": Platform.SENSOR,
                "default": True,
                "required_attribute": "capability",
            },
            "unsupported": {
                "type": Platform.SENSOR,
                "default": True,
                "models": ["OTHER"],
            },
            "wrong": {"type": Platform.SWITCH, "default": True},
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device, sensors=["plain"])
    coordinator = Mock()
    coordinator.async_refresh = AsyncMock()
    with patch(
        "custom_components.midea_ac_lan.sensor.create_cloud_coordinator",
        return_value=coordinator,
    ) as create:
        await async_setup_entry(hass, entry, add_entities)

    added = add_entities.call_args.args[0]
    assert [type(item) for item in added] == [
        MideaCloudUsageSensor,
        MideaCloudUsageSensor,
        MideaEstimatedUsageSensor,
        MideaMinuteDurationSensor,
        MideaFlagStateSensor,
        MideaSensor,
    ]
    assert added[0]._coordinator is coordinator
    assert added[1]._coordinator is coordinator
    create.assert_called_once_with(hass, entry, device.device_id, device.name)
    coordinator.async_refresh.assert_awaited_once_with()


async def test_async_setup_entry_skips_unconfigured_cloud_once(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Skip all cloud sensors after the first missing-account result."""
    install_config(
        {
            "cloud_one": {
                "type": Platform.SENSOR,
                "default": True,
                "cloud_report": "energy",
            },
            "cloud_two": {
                "type": Platform.SENSOR,
                "default": True,
                "cloud_report": "water",
            },
        },
    )
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device)
    with patch(
        "custom_components.midea_ac_lan.sensor.create_cloud_coordinator",
        return_value=None,
    ) as create:
        await async_setup_entry(hass, entry, add_entities)
    create.assert_called_once_with(hass, entry, device.device_id, device.name)
    add_entities.assert_called_once_with([])


def make_sensor(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    config: dict[str, object],
    value: object,
) -> tuple[MideaSensor, Mock, dict[object, object]]:
    """Create a plain sensor with mutable backing state."""
    install_config({"value": {"type": Platform.SENSOR, **config}})
    device, values = device_factory(attributes={"value": value})
    return MideaSensor(device, "value"), device, values


def test_sensor_native_values_and_metadata(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map missing/enum values and expose all configured sensor metadata."""
    sensor, _, values = make_sensor(
        device_factory,
        install_config,
        {
            "missing_values": [-1],
            "options": {1: "one", 2: "two"},
            "device_class": SensorDeviceClass.ENUM,
            "state_class": SensorStateClass.MEASUREMENT,
            "unit": "units",
            "suggested_display_precision": 2,
            "suggested_unit": "suggested",
        },
        -1,
    )
    assert sensor.native_value is None
    values["value"] = 1
    assert sensor.native_value == "one"
    values["value"] = 3
    assert sensor.native_value is None
    values["value"] = object()
    assert sensor.native_value is values["value"]
    assert sensor.device_class is SensorDeviceClass.ENUM
    assert sensor.state_class is SensorStateClass.MEASUREMENT
    assert sensor.options == ["one", "two"]
    assert sensor.native_unit_of_measurement == "units"
    assert sensor.suggested_display_precision == 2
    assert sensor.suggested_unit_of_measurement == "suggested"
    assert sensor.capability_attributes == {"options": ["one", "two"]}


def test_sensor_capability_attributes_without_enum(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose state class only for non-enum sensors and otherwise an empty map."""
    sensor, _, _ = make_sensor(
        device_factory,
        install_config,
        {"state_class": SensorStateClass.TOTAL},
        1,
    )
    assert sensor.options is None
    assert sensor.capability_attributes == {"state_class": SensorStateClass.TOTAL}
    sensor._config.pop("state_class")
    assert sensor.capability_attributes == {}


@pytest.mark.parametrize(
    ("timer", "last_update", "expected"),
    [
        ("down", None, 10),
        ("down", 98.0, 8),
        ("down", 80.0, 0),
        ("up", 98.0, 12),
        ("other", 98.0, 10),
    ],
)
def test_timer_native_value(
    timer: str,
    last_update: float | None,
    expected: int,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Calculate countdown and count-up sensor values from elapsed time."""
    sensor, _, _ = make_sensor(
        device_factory,
        install_config,
        {"timer": timer},
        10,
    )
    sensor._timer_last_update = last_update
    with patch(
        "custom_components.midea_ac_lan.sensor.time",
        SimpleNamespace(time=Mock(return_value=100.0)),
    ):
        assert sensor.native_value == expected


async def test_timer_lifecycle_and_updates(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Start, reset, tick, and cancel configured timer tracking."""
    sensor, device, values = make_sensor(
        device_factory,
        install_config,
        {"timer": "down"},
        10,
    )
    sensor.hass = Mock()
    listener = Mock()
    with (
        patch(
            "custom_components.midea_ac_lan.sensor.time",
            SimpleNamespace(time=Mock(return_value=100.0)),
        ),
        patch(
            "custom_components.midea_ac_lan.sensor.async_track_time_interval",
            return_value=listener,
        ) as track,
    ):
        await sensor.async_added_to_hass()
    assert sensor._timer_base_value == 10
    assert sensor._timer_last_update == pytest.approx(100.0)
    track.assert_called_once()
    device.register_update.assert_called_once_with(sensor.update_state)

    sensor.schedule_update_if_running = Mock()
    values["value"] = 8
    with patch(
        "custom_components.midea_ac_lan.sensor.time",
        SimpleNamespace(time=Mock(return_value=102.0)),
    ):
        sensor.update_state({"value": 8})
    assert sensor._timer_base_value == 8
    assert sensor._timer_last_update == pytest.approx(102.0)
    sensor.schedule_update_if_running.assert_called_once_with()

    sensor.schedule_update_ha_state = Mock()
    sensor._async_timer_update(None)
    sensor.schedule_update_ha_state.assert_called_once_with()
    await sensor.async_will_remove_from_hass()
    listener.assert_called_once_with()
    assert sensor._timer_listener is None
    device.unregister_update.assert_called_once_with(sensor.update_state)


async def test_timer_lifecycle_non_integer_and_no_listener(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Do not seed timer state from non-integer values or cancel a missing listener."""
    sensor, _, _ = make_sensor(
        device_factory,
        install_config,
        {"timer": "down"},
        "unknown",
    )
    sensor.hass = Mock()
    with patch(
        "custom_components.midea_ac_lan.sensor.async_track_time_interval",
        return_value=None,
    ):
        await sensor.async_added_to_hass()
    assert sensor._timer_base_value is None
    sensor.update_state({"value": "unknown"})
    await sensor.async_will_remove_from_hass()

    plain, _, _ = make_sensor(device_factory, install_config, {}, 1)
    await plain.async_added_to_hass()
    await plain.async_will_remove_from_hass()


def test_cloud_usage_sensor(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Read value, availability, date, and update callbacks from the coordinator."""
    install_config(
        {
            "usage": {
                "type": Platform.SENSOR,
                "cloud_report": "energy",
            },
        },
    )
    device, _ = device_factory()
    coordinator = Mock()
    coordinator.data = None
    coordinator.last_update_success = True
    sensor = MideaCloudUsageSensor(device, "usage", coordinator)
    assert sensor.native_value is None
    assert not sensor.available
    assert sensor.extra_state_attributes == {}

    coordinator.data = SimpleNamespace(energy=12.5, report_date=date(2026, 1, 2))
    assert sensor.native_value == pytest.approx(12.5)
    assert sensor.available
    assert sensor.extra_state_attributes == {"report_date": "2026-01-02"}
    coordinator.last_update_success = False
    assert not sensor.available
    sensor.schedule_update_if_running = Mock()
    sensor._handle_coordinator_update()
    sensor.schedule_update_if_running.assert_called_once_with()


async def test_cloud_usage_sensor_subscription(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Register the coordinator listener for removal with the entity."""
    install_config(
        {"usage": {"type": Platform.SENSOR, "cloud_report": "energy"}},
    )
    device, _ = device_factory()
    coordinator = Mock()
    remove = Mock()
    coordinator.async_add_listener.return_value = remove
    sensor = MideaCloudUsageSensor(device, "usage", coordinator)
    sensor.async_on_remove = Mock()
    await sensor.async_added_to_hass()
    coordinator.async_add_listener.assert_called_once_with(
        sensor._handle_coordinator_update,
    )
    sensor.async_on_remove.assert_called_once_with(remove)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(None, None), (-5, 0), (0, 0), (60, 1.0), (61, 1.016667)],
)
def test_minute_duration_sensor(
    raw: int | None,
    expected: float | None,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Convert whole minutes to stable decimal hours and preserve exact minutes."""
    install_config({"duration": {"type": Platform.SENSOR}})
    device, _ = device_factory(attributes={"duration": raw})
    sensor = MideaMinuteDurationSensor(device, "duration")
    if isinstance(expected, float):
        assert sensor.native_value == pytest.approx(expected)
    else:
        assert sensor.native_value == expected
    assert sensor.extra_state_attributes == {"remaining_minutes": max(0, raw or 0)}


def test_flag_state_sensor(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Select the first active flag and refresh for mapped flag reports."""
    install_config(
        {
            "state": {
                "type": Platform.SENSOR,
                "device_class": SensorDeviceClass.ENUM,
                "state_from_flags": {"heating": "heat", "cooling": "cool"},
            },
        },
    )
    device, values = device_factory(
        attributes={"heating": False, "cooling": True},
    )
    sensor = MideaFlagStateSensor(device, "state")
    assert sensor.native_value == "cool"
    assert sensor.options == ["heat", "cool"]
    values["heating"] = True
    assert sensor.native_value == "heat"
    values["heating"] = False
    values["cooling"] = False
    assert sensor.native_value is None
    sensor.hass = Mock()
    sensor.schedule_update_if_running = Mock()
    sensor.update_state({"cooling": False})
    sensor.schedule_update_if_running.assert_called_once_with()
    sensor.update_state({"unrelated": True})
    sensor.schedule_update_if_running.assert_called_once_with()

    sensor._config["device_class"] = SensorDeviceClass.TEMPERATURE
    assert sensor.options is None
    detached = MideaFlagStateSensor(device, "state")
    detached.schedule_update_if_running = Mock()
    detached.update_state({"heating": True})
    detached.schedule_update_if_running.assert_not_called()


def estimated_device(
    values: dict[str, object],
    *,
    model: str = "TEST-MODEL",
) -> Mock:
    """Build an E1-spec mock so estimated sensor mode lookup uses the public API."""
    device = Mock(spec=MideaE1Device)
    device.device_type = TEST_DEVICE_TYPE
    device.device_id = 123456
    device.name = "Dishwasher"
    device.model = model
    device.subtype = 1
    device.available = True
    device.attributes = values
    device.mac = None
    device.serial_number = None
    device.modes = {1: "eco", 2: "intensive"}
    device.get_attribute.side_effect = values.get
    return device


def estimated_config() -> dict[str, object]:
    """Return a representative fixed per-cycle estimate configuration."""
    return {
        "type": Platform.SENSOR,
        "estimate": {
            "values_by_model": {
                "TEST-MODEL": {1: 1.2345, 3: 2.5},
            },
        },
    }


@pytest.mark.parametrize(("restored", "expected"), [("2.5", 2.5), ("bad", 0.0)])
async def test_estimated_usage_restore(
    restored: str,
    expected: float,
    install_config: InstallConfig,
) -> None:
    """Restore a valid accumulated estimate and reset malformed state."""
    install_config({"usage": estimated_config()})
    values: dict[str, object] = {
        "progress": "washing",
        "status": "running",
        "mode": "eco",
    }
    device = estimated_device(values)
    sensor = MideaEstimatedUsageSensor(device, "usage")
    sensor.async_get_last_state = AsyncMock(
        return_value=SimpleNamespace(state=restored),
    )
    await sensor.async_added_to_hass()
    assert sensor.native_value == pytest.approx(expected)
    assert sensor._last_progress == "washing"
    assert sensor._running_mode == "eco"


async def test_estimated_usage_restore_without_state(
    install_config: InstallConfig,
) -> None:
    """Start at zero and do not capture a mode when the appliance is idle."""
    install_config({"usage": estimated_config()})
    device = estimated_device({"progress": None, "status": "idle", "mode": "eco"})
    sensor = MideaEstimatedUsageSensor(device, "usage")
    sensor.async_get_last_state = AsyncMock(return_value=None)
    await sensor.async_added_to_hass()
    assert sensor.native_value == pytest.approx(0)
    assert sensor._running_mode is None


def test_estimated_usage_metadata_and_helpers(
    install_config: InstallConfig,
) -> None:
    """Expose known modes and handle unknown models, devices, and mode names."""
    install_config({"usage": estimated_config()})
    device = estimated_device({})
    sensor = MideaEstimatedUsageSensor(device, "usage")
    sensor._native_value = 1.23456
    sensor._last_progress = "complete"
    sensor._running_mode = "eco"
    assert sensor.native_value == pytest.approx(1.235)
    assert sensor.extra_state_attributes == {
        "estimate_source": "fixed_per_wash_mode",
        "known_modes": ["eco", "3"],
        "last_progress": "complete",
        "running_mode": "eco",
    }
    assert sensor._mode_code("eco") == 1
    assert sensor._mode_code("missing") is None
    device.model = "OTHER"
    assert sensor._values() == {}

    plain = Mock()
    plain.device_type = TEST_DEVICE_TYPE
    plain.device_id = 2
    plain.name = "Plain"
    plain.model = "TEST-MODEL"
    plain.subtype = 1
    plain.available = True
    plain.mac = None
    plain.serial_number = None
    plain.attributes = {}
    plain.get_attribute.return_value = None
    plain_sensor = MideaEstimatedUsageSensor(plain, "usage")
    assert plain_sensor._modes() == {}


def test_estimated_usage_accumulates_once(
    install_config: InstallConfig,
) -> None:
    """Capture running mode and count only the edge into complete progress."""
    install_config({"usage": estimated_config()})
    values: dict[str, object] = {
        "progress": "washing",
        "status": "running",
        "mode": "eco",
    }
    device = estimated_device(values)
    sensor = MideaEstimatedUsageSensor(device, "usage")
    sensor.hass = Mock()
    sensor.schedule_update_if_running = Mock()

    sensor.update_state({"status": "running"})
    assert sensor._running_mode == "eco"
    values.update(progress="complete", status="idle", mode=None)
    sensor.update_state({"progress": "complete"})
    assert sensor.native_value == pytest.approx(1.234)
    assert sensor._running_mode is None
    sensor.update_state({"progress": "complete"})
    assert sensor.native_value == pytest.approx(1.234)
    assert sensor.schedule_update_if_running.call_count == 3

    values.update(progress="washing", status="idle", mode="missing")
    sensor.update_state({"mode": "missing"})
    values["progress"] = "complete"
    sensor.update_state({"progress": "complete"})
    assert sensor.native_value == pytest.approx(1.234)
    sensor.update_state({"unrelated": True})
    assert sensor.schedule_update_if_running.call_count == 5


def test_estimated_usage_detached_update(
    install_config: InstallConfig,
) -> None:
    """Accumulate state without scheduling HA writes before attachment."""
    install_config({"usage": estimated_config()})
    values: dict[str, object] = {
        "progress": "complete",
        "status": "idle",
        "mode": "eco",
    }
    sensor = MideaEstimatedUsageSensor(estimated_device(values), "usage")
    sensor.schedule_update_if_running = Mock()
    sensor.update_state({"progress": "complete"})
    sensor.schedule_update_if_running.assert_not_called()


AC_ENTITIES = cast("dict[str, Any]", MIDEA_DEVICES[0xAC]["entities"])
TARGET_HUMIDITY_CONFIG = AC_ENTITIES["target_humidity"]


@pytest.mark.parametrize(
    ("model", "subtype", "expected"),
    [
        ("22396933", 1, True),
        ("22396945", 1, True),
        ("22396937", 0, True),
        ("22396933", 2, False),
        ("OTHER", 1, False),
    ],
)
def test_target_humidity_registry_gate(
    model: str,
    subtype: int,
    expected: bool,
) -> None:
    """Gate the target humidity sensor to the verified AC models and subtypes."""
    assert supports_device(model, subtype, TARGET_HUMIDITY_CONFIG) is expected


def test_target_humidity_native_value(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Pass the parsed percentage through and map zero to unknown."""
    install_config({"target_humidity": TARGET_HUMIDITY_CONFIG})
    device, values = device_factory(attributes={"target_humidity": 50})
    entity = MideaSensor(device, "target_humidity")

    assert entity.native_value == 50
    values["target_humidity"] = 60
    assert entity.native_value == 60
    values["target_humidity"] = 0
    assert entity.native_value is None
    values["target_humidity"] = None
    assert entity.native_value is None
