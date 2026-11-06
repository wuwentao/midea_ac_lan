"""Tests for the shared Midea entity base class."""

from types import SimpleNamespace
from unittest.mock import Mock

import homeassistant.const as ha_const
import homeassistant.helpers.entity as ha_entity
import pytest
from homeassistant.const import Platform
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory

from custom_components.midea_ac_lan.const import DOMAIN
from custom_components.midea_ac_lan.midea_entity import MideaEntity

from .helpers import DeviceFactory, InstallConfig, load_integration_module


def test_legacy_device_info_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keep the pre-2023.9 DeviceInfo import fallback executable."""
    monkeypatch.setattr(ha_const, "MAJOR_VERSION", 2023)
    monkeypatch.setattr(ha_const, "MINOR_VERSION", 8)
    monkeypatch.setattr(ha_entity, "DeviceInfo", DeviceInfo, raising=False)

    module = load_integration_module("midea_entity", "legacy_device_info")

    assert module.DeviceInfo is DeviceInfo


@pytest.mark.parametrize(
    ("config", "model", "expected_name", "expected_translation"),
    [
        ({"translation_key": "power"}, "A", None, "power"),
        (
            {
                "translation_key": "power",
                "translation_key_by_model": {"A": "model_power"},
            },
            "A",
            None,
            "model_power",
        ),
        ({"name": "Explicit"}, "A", "Explicit", None),
        ({"device_class": "temperature"}, "A", None, None),
        ({}, "A", None, None),
    ],
)
def test_init_name_precedence(
    config: dict[str, object],
    model: str,
    expected_name: str | None,
    expected_translation: str | None,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Apply model translations before explicit and fallback names."""
    install_config({"value": {"type": Platform.SENSOR, **config}})
    device, _ = device_factory(model=model)

    entity = MideaEntity(device, "value")

    assert getattr(entity, "_attr_name", None) == expected_name
    assert entity._attr_translation_key == expected_translation
    assert entity._attr_has_entity_name
    assert entity.entity_id == "sensor.123456_value"


def test_init_registry_hints_and_mapped_attributes(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Copy entity registry hints and read/write attribute mappings."""
    install_config(
        {
            "control": {
                "type": Platform.SWITCH,
                "attribute": "write_value",
                "state_attribute": "read_value",
                "entity_category": EntityCategory.CONFIG,
                "entity_registry_enabled_default": False,
                "icon": "mdi:test-tube",
            },
        },
    )
    device, _ = device_factory()

    entity = MideaEntity(device, "control")

    assert entity._attribute_key == "write_value"
    assert entity._state_attribute_key == "read_value"
    assert entity._attr_entity_category is EntityCategory.CONFIG
    assert not entity._attr_entity_registry_enabled_default
    assert entity.icon == "mdi:test-tube"


def test_identity_and_device_info(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose stable IDs and complete Home Assistant device information."""
    install_config({"value": {"type": Platform.SENSOR}})
    device, _ = device_factory(model="Model X", subtype=7)
    entity = MideaEntity(device, "value")

    assert entity.device is device
    assert entity.unique_id == f"{DOMAIN}.123456_value"
    assert not entity.should_poll
    assert entity.device_info == {
        "manufacturer": "Midea",
        "model": "Test appliance Model X (7)",
        "identifiers": {(DOMAIN, "123456")},
        "name": "Test appliance",
        "connections": {("mac", "aa:bb:cc:dd:ee:ff")},
        "serial_number": "00000000000000000000000000000000",
    }

    device.mac = None
    device.serial_number = None
    assert "connections" not in entity.device_info
    assert "serial_number" not in entity.device_info


@pytest.mark.parametrize(
    ("device_available", "values", "config", "expected"),
    [
        (False, {}, {}, False),
        (True, {}, {}, True),
        (True, {"capable": False}, {"available_attribute": "capable"}, False),
        (True, {"capable": True}, {"available_attribute": "capable"}, True),
        (
            True,
            {"capable": True, "value": None},
            {
                "available_attribute": "capable",
                "available_value_attribute": "value",
            },
            False,
        ),
        (
            True,
            {"capable": True, "value": 0},
            {
                "available_attribute": "capable",
                "available_value_attribute": "value",
            },
            True,
        ),
    ],
)
def test_available(
    device_available: bool,
    values: dict[str, object],
    config: dict[str, object],
    expected: bool,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Combine device, capability, and value availability."""
    install_config({"value": {"type": Platform.SENSOR, **config}})
    device, _ = device_factory(attributes=values, available=device_available)
    assert MideaEntity(device, "value").available is expected


async def test_update_subscription_lifecycle(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Register and unregister the callback with the device lifecycle."""
    install_config({"value": {"type": Platform.SENSOR}})
    device, _ = device_factory()
    entity = MideaEntity(device, "value")

    await entity.async_added_to_hass()
    await entity.async_will_remove_from_hass()

    device.register_update.assert_called_once_with(entity.update_state)
    device.unregister_update.assert_called_once_with(entity.update_state)


def test_schedule_update_guards_and_success(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Skip writes during shutdown or after loop close, otherwise schedule."""
    install_config({"value": {"type": Platform.SENSOR}})
    device, _ = device_factory()
    entity = MideaEntity(device, "value")
    entity.schedule_update_ha_state = Mock()
    loop = Mock()
    loop.is_closed.return_value = False
    entity.hass = SimpleNamespace(is_stopping=True, loop=loop)
    entity.schedule_update_if_running()
    entity.schedule_update_ha_state.assert_not_called()

    entity.hass.is_stopping = False
    loop.is_closed.return_value = True
    entity.schedule_update_if_running()
    entity.schedule_update_ha_state.assert_not_called()

    loop.is_closed.return_value = False
    entity.schedule_update_if_running()
    entity.schedule_update_ha_state.assert_called_once_with()


def test_schedule_update_runtime_error_paths(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Only swallow RuntimeError when the loop closed during scheduling."""
    install_config({"value": {"type": Platform.SENSOR}})
    device, _ = device_factory()
    entity = MideaEntity(device, "value")
    entity.schedule_update_ha_state = Mock(side_effect=RuntimeError("closed"))
    loop = Mock()
    loop.is_closed.side_effect = [False, True]
    entity.hass = SimpleNamespace(is_stopping=False, loop=loop)
    entity.schedule_update_if_running()

    loop.is_closed.side_effect = None
    loop.is_closed.return_value = False
    with pytest.raises(RuntimeError, match="closed"):
        entity.schedule_update_if_running()


def test_update_state_filters_reports(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Refresh only for state or availability-related reports."""
    install_config(
        {
            "control": {
                "type": Platform.SWITCH,
                "state_attribute": "reported",
                "available_attribute": "capable",
            },
        },
    )
    device, _ = device_factory()
    entity = MideaEntity(device, "control")
    entity.hass = Mock()
    entity.schedule_update_if_running = Mock()

    entity.update_state({"reported": True})
    entity.update_state({"available": True})
    entity.update_state({"capable": True})
    assert entity.schedule_update_if_running.call_count == 3

    entity.update_state({"unrelated": True})
    assert entity.schedule_update_if_running.call_count == 3

    detached = MideaEntity(device, "control")
    detached.schedule_update_if_running = Mock()
    detached.update_state({"reported": False})
    assert entity.schedule_update_if_running.call_count == 3
    detached.schedule_update_if_running.assert_not_called()
