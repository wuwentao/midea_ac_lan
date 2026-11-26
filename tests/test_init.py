"""Tests for integration setup, lifecycle, services, and migration."""

import asyncio
from enum import StrEnum
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SWITCHES,
    CONF_TOKEN,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from midealan.device import DeviceType, MideaDevice, ProtocolVersion

from custom_components import midea_ac_lan
from custom_components.midea_ac_lan.const import (
    ALL_PLATFORM,
    CONF_ACCOUNT,
    CONF_CLOUD_NAME,
    CONF_KEY,
    CONF_MAC,
    CONF_MANUFACTURER_CODE,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL,
    CONF_SN,
    CONF_SN8,
    CONF_SUBTYPE,
    DEVICES,
    DOMAIN,
)


class Attribute(StrEnum):
    """Non-string registry key used to cover enum-backed attributes."""

    POWER = "power"


async def test_close_device_success_and_expected_errors() -> None:
    """Close normally and absorb connection cleanup failures."""
    device = Mock()
    device.close = AsyncMock()
    await midea_ac_lan._close_device(device)
    device.close.assert_awaited_once_with()
    for error in (OSError("socket"), ConnectionError("closed"), AttributeError("old")):
        device.close.reset_mock(side_effect=True)
        device.close.side_effect = error
        await midea_ac_lan._close_device(device)


def test_device_store_initializes_nested_mapping() -> None:
    """Create and reuse the integration device store."""
    hass = SimpleNamespace(data={})
    store = midea_ac_lan._device_store(hass)
    assert store == {}
    store[1] = Mock()
    assert midea_ac_lan._device_store(hass) is store


def test_remove_unsupported_entities() -> None:
    """Remove current and legacy entity IDs only for unsupported configs."""
    device = Mock(spec=MideaDevice)
    device.device_type = 1
    device.device_id = 42
    device.model = "MODEL"
    device.subtype = 1
    registry = Mock()
    registry.async_get_entity_id.side_effect = [
        None,
        "sensor.current",
        None,
    ]
    registry.async_get.side_effect = [Mock(), None]
    configs = {
        "supported": {"type": Platform.SENSOR},
        "legacy": {"type": Platform.SENSOR, "models": ["OTHER"]},
        "current": {"type": Platform.SENSOR, "models": ["OTHER"]},
        "missing": {"type": Platform.SENSOR, "models": ["OTHER"]},
    }
    with (
        patch.object(midea_ac_lan, "MIDEA_DEVICES", {1: {"entities": configs}}),
        patch("custom_components.midea_ac_lan.er.async_get", return_value=registry),
    ):
        midea_ac_lan._remove_unsupported_entities(
            Mock(),
            device,
        )
    assert registry.async_remove.call_args_list == [
        call("sensor.42_legacy"),
        call("sensor.current"),
    ]


async def test_update_listener_reloads_entry() -> None:
    """Reload the changed config entry."""
    hass = Mock()
    hass.config_entries.async_reload = AsyncMock()
    entry = SimpleNamespace(entry_id="entry")
    await midea_ac_lan.update_listener(hass, entry)
    hass.config_entries.async_reload.assert_awaited_once_with("entry")


async def test_async_setup_registers_and_runs_services(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Register service schemas and exercise valid and invalid service calls."""
    hass = Mock()
    hass.data = {}
    hass.services.async_register = Mock()
    registry = {
        1: {
            "entities": {
                Attribute.POWER: {"type": Platform.SWITCH},
                "mapped": {
                    "type": Platform.SWITCH,
                    "attribute": "target",
                },
                "sensor": {"type": Platform.SENSOR},
            },
        },
    }
    monkeypatch.setattr(midea_ac_lan, "MIDEA_DEVICES", registry)
    monkeypatch.setattr(
        midea_ac_lan,
        "_ATTRIBUTE_ALIASES",
        {1: {"legacy_mapped": "mapped"}},
    )
    assert await midea_ac_lan.async_setup(hass, {})

    assert hass.services.async_register.call_count == 2
    set_attribute = hass.services.async_register.call_args_list[0].args[2]
    set_attribute_schema = hass.services.async_register.call_args_list[0].kwargs[
        "schema"
    ]
    send_command = hass.services.async_register.call_args_list[1].args[2]
    device = Mock()
    device.device_type = 1
    hass.data[DOMAIN][DEVICES] = {7: device}

    set_attribute(
        SimpleNamespace(data={"device_id": 7, "attribute": "mapped", "value": 3}),
    )
    device.set_attribute.assert_called_once_with(attr="target", value=3)
    device.set_attribute.reset_mock()
    legacy_service_data = set_attribute_schema(
        {"device_id": 7, "attribute": "legacy_mapped", "value": 4},
    )
    set_attribute(SimpleNamespace(data=legacy_service_data))
    device.set_attribute.assert_called_once_with(attr="target", value=4)
    device.set_attribute.reset_mock()
    set_attribute(
        SimpleNamespace(data={"device_id": 7, "attribute": "sensor", "value": 3}),
    )
    device.set_attribute.assert_not_called()

    device.device_type = DeviceType.AC
    set_attribute(
        SimpleNamespace(
            data={"device_id": 7, "attribute": "fan_speed", "value": "auto"},
        ),
    )
    device.set_attribute.assert_called_once_with(attr="fan_speed", value=102)
    device.set_attribute.reset_mock()
    set_attribute(
        SimpleNamespace(data={"device_id": 7, "attribute": "fan_speed", "value": 102}),
    )
    device.set_attribute.assert_called_once_with(attr="fan_speed", value=102)
    device.set_attribute.reset_mock()
    set_attribute(
        SimpleNamespace(data={"device_id": 7, "attribute": "fan_speed", "value": 103}),
    )
    device.set_attribute.assert_not_called()
    set_attribute(
        SimpleNamespace(data={"device_id": 999, "attribute": "mapped", "value": 1}),
    )

    send_command(
        SimpleNamespace(data={"device_id": 7, "cmd_type": 2, "cmd_body": "01ff"}),
    )
    device.send_command.assert_called_once_with(2, bytearray.fromhex("01ff"))
    send_command(
        SimpleNamespace(data={"device_id": 7, "cmd_type": 2, "cmd_body": "invalid"}),
    )
    assert device.send_command.call_count == 1
    send_command(
        SimpleNamespace(data={"device_id": 999, "cmd_type": 2, "cmd_body": "01"}),
    )


def entry_data(**overrides: object) -> dict[str, object]:
    """Build a complete config-entry data mapping."""
    data: dict[str, object] = {
        CONF_NAME: "Device",
        CONF_DEVICE_ID: 42,
        CONF_TYPE: 1,
        CONF_PROTOCOL: ProtocolVersion.V2,
        CONF_IP_ADDRESS: "192.0.2.1",
        CONF_PORT: 6444,
        CONF_MODEL: "MODEL",
        CONF_SUBTYPE: 1,
        CONF_TOKEN: "",
        CONF_KEY: "",
        CONF_MAC: "aabbccddeeff",
        CONF_SN: "00000000000000000000000000000000",
        CONF_SN8: "00000000",
        CONF_MANUFACTURER_CODE: "0000",
        CONF_CLOUD_NAME: "SmartHome",
    }
    data.update(overrides)
    return data


def config_entry(
    *,
    data: dict[str, object] | None = None,
    options: dict[str, object] | None = None,
) -> Mock:
    """Build a config entry mock with mutable data and options."""
    entry = Mock()
    entry.data = data or entry_data()
    entry.options = options or {}
    entry.entry_id = "entry"
    entry.version = 2
    entry.minor_version = 2
    entry.add_update_listener.return_value = Mock()
    return entry


def setup_hass(device: Mock | None) -> tuple[Mock, Mock, Mock]:
    """Build Home Assistant lifecycle mocks and captured listener removal."""
    if device is not None:
        # open()/close() became coroutines in the asyncio transport migration.
        device.open = AsyncMock()
        device.close = AsyncMock()
    hass = Mock()
    hass.data = {}
    hass.async_add_import_executor_job = AsyncMock(return_value=device)
    hass.async_add_executor_job = AsyncMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    remove_listener = Mock()
    hass.bus.async_listen_once.return_value = remove_listener
    return hass, remove_listener, hass.config_entries


async def test_async_setup_entry_account_and_invalid_v3() -> None:
    """Skip account entries and reject V3 devices without Token/Key."""
    hass, _, _ = setup_hass(None)
    assert await midea_ac_lan.async_setup_entry(
        hass,
        config_entry(data={CONF_TYPE: CONF_ACCOUNT}),
    )
    invalid = config_entry(
        data=entry_data(**{CONF_PROTOCOL: ProtocolVersion.V3}),
    )
    assert not await midea_ac_lan.async_setup_entry(hass, invalid)
    hass.async_add_import_executor_job.assert_not_awaited()


async def test_async_setup_entry_selector_failure_and_defaults() -> None:
    """Return false when the selector rejects a legacy entry with default fields."""
    hass, _, _ = setup_hass(None)
    entry = config_entry(
        data=entry_data(
            **{
                CONF_NAME: None,
                CONF_TYPE: None,
                CONF_TOKEN: None,
                CONF_KEY: None,
                CONF_SN: None,
                CONF_MAC: None,
            },
        ),
    )
    assert not await midea_ac_lan.async_setup_entry(hass, entry)
    args = hass.async_add_import_executor_job.await_args.args
    assert args[1] == "42"
    assert args[3] == 0xAC


async def test_async_setup_entry_success_and_stop_cleanup() -> None:
    """Open, register, forward, refresh, close on stop, and attach unload callbacks."""
    device = Mock()
    device.device_type = 1
    device.device_id = 42
    device.model = "MODEL"
    device.subtype = 1
    hass, remove_listener, config_entries = setup_hass(device)
    entry = config_entry(
        options={
            CONF_IP_ADDRESS: "192.0.2.2",
            CONF_REFRESH_INTERVAL: 15,
            CONF_CUSTOMIZE: "{}",
        },
    )
    with (
        patch.object(midea_ac_lan, "MIDEA_DEVICES", {1: {"entities": {}}}),
        patch.object(midea_ac_lan, "_remove_unsupported_entities") as remove_stale,
    ):
        assert await midea_ac_lan.async_setup_entry(hass, entry)

    device.set_refresh_interval.assert_called_once_with(15)
    device.open.assert_awaited_once_with()
    assert hass.data[DOMAIN][DEVICES][42] is device
    config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry,
        ALL_PLATFORM,
    )
    remove_stale.assert_called_once_with(hass, device)
    hass.bus.async_listen_once.assert_called_once()
    assert hass.bus.async_listen_once.call_args.args[0] == EVENT_HOMEASSISTANT_STOP
    stop_callback = hass.bus.async_listen_once.call_args.args[1]
    await stop_callback(Mock())
    # _async_close_on_stop awaits _close_device(device) directly, which awaits
    # the now-coroutine device.close() instead of offloading to an executor.
    device.close.assert_awaited_once_with()
    assert entry.async_on_unload.call_args_list == [
        call(remove_listener),
        call(entry.add_update_listener.return_value),
    ]
    entry.add_update_listener.assert_called_once_with(midea_ac_lan.update_listener)


@pytest.mark.parametrize("error", [RuntimeError("forward"), asyncio.CancelledError()])
async def test_async_setup_entry_forward_failure_cleanup(error: BaseException) -> None:
    """Detach the stop listener, drop the store entry, close, and re-raise."""
    device = Mock()
    device.device_type = 1
    device.device_id = 42
    device.model = "MODEL"
    device.subtype = 1
    hass, remove_listener, _ = setup_hass(device)
    hass.config_entries.async_forward_entry_setups.side_effect = error
    entry = config_entry()
    with (
        patch.object(midea_ac_lan, "MIDEA_DEVICES", {1: {"entities": {}}}),
        patch.object(midea_ac_lan, "_remove_unsupported_entities"),
        pytest.raises(type(error)),
    ):
        await midea_ac_lan.async_setup_entry(hass, entry)
    remove_listener.assert_called_once_with()
    assert 42 not in hass.data[DOMAIN][DEVICES]
    # Forward-failure cleanup awaits _close_device(device) directly now.
    device.close.assert_awaited_once_with()


@pytest.mark.parametrize(
    ("unload_result", "device_id", "expect_close"),
    [(False, 42, False), (True, None, False), (True, 42, True)],
)
async def test_async_unload_entry(
    unload_result: bool,
    device_id: int | None,
    expect_close: bool,
) -> None:
    """Only remove and close a device after successful platform unload."""
    device = Mock()
    hass, _, _ = setup_hass(device)
    hass.data = {DOMAIN: {DEVICES: {42: device}}}
    hass.config_entries.async_unload_platforms.return_value = unload_result
    data = entry_data()
    data[CONF_DEVICE_ID] = device_id
    entry = config_entry(data=data)
    assert await midea_ac_lan.async_unload_entry(hass, entry) is unload_result
    assert device.close.called is expect_close


async def test_async_unload_entry_missing_loaded_device() -> None:
    """Succeed when platforms unload but the device was already removed."""
    hass, _, _ = setup_hass(None)
    hass.data = {DOMAIN: {DEVICES: {}}}
    assert await midea_ac_lan.async_unload_entry(
        hass,
        config_entry(data=entry_data(**{CONF_DEVICE_ID: 999})),
    )


async def test_async_unload_account_entry() -> None:
    """Unload an account-only entry without touching platforms."""
    hass, _, _ = setup_hass(None)
    assert await midea_ac_lan.async_unload_entry(
        hass,
        config_entry(data={CONF_TYPE: CONF_ACCOUNT}),
    )
    hass.config_entries.async_unload_platforms.assert_not_awaited()


async def test_async_migrate_entry_versions() -> None:
    """Migrate v1 identifiers and successful v2.1 identity backfill."""
    hass = Mock()
    entry = config_entry()
    entry.version = 1
    with patch(
        "custom_components.midea_ac_lan._async_migrate_device_identifiers",
        new_callable=AsyncMock,
    ) as migrate_ids:
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
    hass.config_entries.async_update_entry.assert_called_once_with(entry, version=2)
    migrate_ids.assert_awaited_once_with(hass, entry)

    hass.reset_mock()
    entry.version = 2
    entry.minor_version = 1
    with patch(
        "custom_components.midea_ac_lan._async_backfill_mac_and_sn",
        new_callable=AsyncMock,
        return_value=True,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
    assert hass.config_entries.async_update_entry.call_args_list == [
        call(entry, minor_version=2),
        call(entry, minor_version=3),
    ]

    hass.reset_mock()
    with patch(
        "custom_components.midea_ac_lan._async_backfill_mac_and_sn",
        new_callable=AsyncMock,
        return_value=False,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
    hass.config_entries.async_update_entry.assert_not_called()


async def test_function_num_migration_survives_backfill_retry() -> None:
    """Rename cooking controls while retaining 2.1 identity retry state."""
    hass = Mock()
    entry = config_entry(
        data=entry_data(**{CONF_TYPE: DeviceType.EB}),
        options={CONF_SWITCHES: ["function_no", "work_status"]},
    )
    entry.minor_version = 1
    registry = Mock()
    registry.async_get_entity_id.return_value = "number.42_function_no"

    with (
        patch(
            "custom_components.midea_ac_lan._async_backfill_mac_and_sn",
            new_callable=AsyncMock,
            return_value=False,
        ) as backfill,
        patch(
            "custom_components.midea_ac_lan.er.async_get",
            return_value=registry,
        ),
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
        backfill.assert_awaited_once_with(hass, entry)

        registry.async_update_entity.assert_called_once_with(
            "number.42_function_no",
            new_unique_id=f"{DOMAIN}.42_function_num",
        )
        hass.config_entries.async_update_entry.assert_called_once_with(
            entry,
            options={CONF_SWITCHES: ["function_num", "work_status"]},
        )
        assert entry.minor_version == 1

        entry.options = {CONF_SWITCHES: ["function_num", "work_status"]}
        hass.reset_mock()
        registry.reset_mock()
        registry.async_get_entity_id.return_value = None
        registry.async_get.return_value = None
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    assert backfill.await_count == 2
    registry.async_update_entity.assert_not_called()
    hass.config_entries.async_update_entry.assert_not_called()
    assert entry.minor_version == 1


async def test_function_num_chained_migration_is_stateful_and_idempotent() -> None:
    """Apply the full 2.1-to-2.3 migration and keep the existing entity ID."""
    hass = Mock()
    entry = config_entry(
        data=entry_data(**{CONF_TYPE: DeviceType.E7}),
        options={CONF_SWITCHES: ["function_no", "work_status"]},
    )
    entry.minor_version = 1
    legacy_unique_id = f"{DOMAIN}.42_function_no"
    current_unique_id = f"{DOMAIN}.42_function_num"
    existing_entity_id = "number.42_function_no"
    entities = {legacy_unique_id: existing_entity_id}

    def update_entry(updated_entry: Mock, **changes: object) -> None:
        for key, value in changes.items():
            setattr(updated_entry, key, value)

    def get_entity_id(_domain: Platform, _platform: str, unique_id: str) -> str | None:
        return entities.get(unique_id)

    def update_entity(entity_id: str, *, new_unique_id: str) -> None:
        assert entity_id == existing_entity_id
        del entities[legacy_unique_id]
        entities[new_unique_id] = entity_id

    hass.config_entries.async_update_entry.side_effect = update_entry
    registry = Mock()
    registry.async_get_entity_id.side_effect = get_entity_id
    registry.async_update_entity.side_effect = update_entity

    with (
        patch(
            "custom_components.midea_ac_lan._async_backfill_mac_and_sn",
            new_callable=AsyncMock,
            return_value=True,
        ) as backfill,
        patch(
            "custom_components.midea_ac_lan.er.async_get",
            return_value=registry,
        ),
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
        assert entry.version == 2
        assert entry.minor_version == 3
        assert entry.options == {
            CONF_SWITCHES: ["function_num", "work_status"],
        }
        assert entities == {current_unique_id: existing_entity_id}

        hass.config_entries.async_update_entry.reset_mock()
        registry.reset_mock()
        backfill.reset_mock()
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    backfill.assert_not_awaited()
    registry.async_update_entity.assert_not_called()
    hass.config_entries.async_update_entry.assert_not_called()
    assert entities == {current_unique_id: existing_entity_id}


@pytest.mark.parametrize("device_type", [DeviceType.E7, DeviceType.EB])
async def test_migrate_function_num_selection_and_entity(
    device_type: DeviceType,
) -> None:
    """Preserve released cooking-device options and entities during the rename."""
    hass = Mock()
    entry = config_entry(
        data=entry_data(**{CONF_TYPE: device_type}),
        options={CONF_SWITCHES: ["function_no", "work_status"]},
    )
    entry.minor_version = 2
    registry = Mock()
    registry.async_get_entity_id.return_value = "number.42_function_no"

    with patch(
        "custom_components.midea_ac_lan.er.async_get",
        return_value=registry,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    registry.async_update_entity.assert_called_once_with(
        "number.42_function_no",
        new_unique_id=f"{DOMAIN}.42_function_num",
    )
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        options={CONF_SWITCHES: ["function_num", "work_status"]},
        minor_version=3,
    )


async def test_migrate_function_num_legacy_entity_id() -> None:
    """Migrate a cooking entity that predates unique-id registry lookup."""
    hass = Mock()
    entry = config_entry(data=entry_data(**{CONF_TYPE: DeviceType.EB}))
    entry.minor_version = 2
    registry = Mock()
    registry.async_get_entity_id.return_value = None
    legacy_entry = Mock()
    legacy_entry.domain = Platform.NUMBER
    legacy_entry.platform = DOMAIN
    legacy_entry.config_entry_id = entry.entry_id
    legacy_entry.unique_id = f"{DOMAIN}.42_function_no"
    registry.async_get.return_value = legacy_entry

    with patch(
        "custom_components.midea_ac_lan.er.async_get",
        return_value=registry,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    registry.async_update_entity.assert_called_once_with(
        "number.42_function_no",
        new_unique_id=f"{DOMAIN}.42_function_num",
    )


@pytest.mark.parametrize(
    ("domain", "platform", "config_entry_id", "unique_id"),
    [
        (Platform.SENSOR, DOMAIN, "entry", f"{DOMAIN}.42_function_no"),
        (Platform.NUMBER, "other_domain", "entry", f"{DOMAIN}.42_function_no"),
        (Platform.NUMBER, DOMAIN, "other_entry", f"{DOMAIN}.42_function_no"),
        (Platform.NUMBER, DOMAIN, "entry", f"{DOMAIN}.42_function_num"),
    ],
)
async def test_migrate_function_num_rejects_unowned_legacy_entity_id(
    domain: Platform,
    platform: str,
    config_entry_id: str,
    unique_id: str,
) -> None:
    """Do not rewrite an entity-ID fallback that is not the legacy entity."""
    hass = Mock()
    entry = config_entry(data=entry_data(**{CONF_TYPE: DeviceType.EB}))
    entry.minor_version = 2
    registry = Mock()
    registry.async_get_entity_id.return_value = None
    legacy_entry = Mock()
    legacy_entry.domain = domain
    legacy_entry.platform = platform
    legacy_entry.config_entry_id = config_entry_id
    legacy_entry.unique_id = unique_id
    registry.async_get.return_value = legacy_entry

    with patch(
        "custom_components.midea_ac_lan.er.async_get",
        return_value=registry,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    registry.async_update_entity.assert_not_called()


@pytest.mark.parametrize("device_id", [None, 42])
async def test_migrate_function_num_without_legacy_entity(
    device_id: int | None,
) -> None:
    """Complete migration when no prior cooking entity registry entry exists."""
    hass = Mock()
    entry = config_entry(
        data=entry_data(
            **{CONF_TYPE: DeviceType.EB, CONF_DEVICE_ID: device_id},
        ),
    )
    entry.minor_version = 2
    registry = Mock()
    registry.async_get_entity_id.return_value = None
    registry.async_get.return_value = None

    with patch(
        "custom_components.midea_ac_lan.er.async_get",
        return_value=registry,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    registry.async_update_entity.assert_not_called()
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        minor_version=3,
    )


async def test_migrate_non_eb_entry_to_minor_version_three() -> None:
    """Advance other device entries without applying EB-specific migration."""
    hass = Mock()
    entry = config_entry(
        data=entry_data(**{CONF_TYPE: DeviceType.AC}),
        options={CONF_SWITCHES: ["function_no"]},
    )
    entry.minor_version = 2

    with patch("custom_components.midea_ac_lan.er.async_get") as async_get_registry:
        assert await midea_ac_lan.async_migrate_entry(hass, entry)

    async_get_registry.assert_not_called()
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        minor_version=3,
    )


@pytest.mark.parametrize(
    "data",
    [
        {CONF_TYPE: CONF_ACCOUNT},
        {CONF_MAC: "aabbccddeeff"},
        {CONF_SN: "00000000000000000000000000000000"},
        {CONF_IP_ADDRESS: None, CONF_DEVICE_ID: 1},
        {CONF_IP_ADDRESS: "192.0.2.1", CONF_DEVICE_ID: None},
    ],
)
async def test_backfill_early_success(data: dict[str, object]) -> None:
    """Skip discovery when identity or lookup fields make it unnecessary."""
    hass = Mock()
    entry = config_entry(data=data)
    assert await midea_ac_lan._async_backfill_mac_and_sn(hass, entry)
    hass.async_add_executor_job.assert_not_called()


async def test_backfill_discovery_results() -> None:
    """Honor option IP, update found identity, and retry missing/error results."""
    data = {
        CONF_TYPE: 1,
        CONF_DEVICE_ID: 42,
        CONF_IP_ADDRESS: "192.0.2.1",
    }
    entry = config_entry(data=data, options={CONF_IP_ADDRESS: "192.0.2.2"})
    hass = Mock()
    hass.async_add_executor_job = AsyncMock(
        return_value={42: {CONF_MAC: "aabb", CONF_SN: "serial"}},
    )
    assert await midea_ac_lan._async_backfill_mac_and_sn(hass, entry)
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        data={**data, CONF_MAC: "aabb", CONF_SN: "serial"},
    )

    hass.async_add_executor_job.return_value = {}
    assert not await midea_ac_lan._async_backfill_mac_and_sn(hass, entry)
    hass.async_add_executor_job.side_effect = OSError("offline")
    assert not await midea_ac_lan._async_backfill_mac_and_sn(hass, entry)


async def test_backfill_executes_discovery_callable() -> None:
    """Run discovery through Home Assistant's executor callable."""
    data = {
        CONF_TYPE: 1,
        CONF_DEVICE_ID: 42,
        CONF_IP_ADDRESS: "192.0.2.1",
    }
    entry = config_entry(data=data)
    hass = Mock()
    hass.async_add_executor_job = AsyncMock(side_effect=lambda target: target())
    with patch.object(
        midea_ac_lan,
        "discover",
        return_value={42: {CONF_MAC: "aabb", CONF_SN: "serial"}},
    ) as discover_mock:
        assert await midea_ac_lan._async_backfill_mac_and_sn(hass, entry)

    discover_mock.assert_called_once_with(ip_address="192.0.2.1")


async def test_migrate_device_identifiers() -> None:
    """Update only the first identifier-bearing device entry."""
    hass = Mock()
    entry = config_entry()
    registry = Mock()
    device_one = SimpleNamespace(id="one", identifiers=[(DOMAIN, 123), ("x", 2)])
    device_two = SimpleNamespace(id="two", identifiers={(DOMAIN, 456)})
    with (
        patch("custom_components.midea_ac_lan.dr.async_get", return_value=registry),
        patch(
            "custom_components.midea_ac_lan.dr.async_entries_for_config_entry",
            return_value=[device_one, device_two],
        ),
    ):
        await midea_ac_lan._async_migrate_device_identifiers(hass, entry)
    registry.async_update_device.assert_called_once_with(
        device_id="one",
        new_identifiers={(DOMAIN, "123")},
    )


async def test_migrate_device_identifiers_without_entries() -> None:
    """Do nothing when the config entry has no device-registry entry."""
    with (
        patch(
            "custom_components.midea_ac_lan.dr.async_get",
            return_value=Mock(),
        ) as get_registry,
        patch(
            "custom_components.midea_ac_lan.dr.async_entries_for_config_entry",
            return_value=[],
        ),
    ):
        await midea_ac_lan._async_migrate_device_identifiers(Mock(), config_entry())
    get_registry.return_value.async_update_device.assert_not_called()


async def test_migrate_device_identifiers_skips_empty_entry() -> None:
    """Continue to the next registry device when one has no identifiers."""
    registry = Mock()
    entries = [
        SimpleNamespace(id="empty", identifiers=[]),
        SimpleNamespace(id="found", identifiers=[(DOMAIN, 456)]),
    ]
    with (
        patch("custom_components.midea_ac_lan.dr.async_get", return_value=registry),
        patch(
            "custom_components.midea_ac_lan.dr.async_entries_for_config_entry",
            return_value=entries,
        ),
    ):
        await midea_ac_lan._async_migrate_device_identifiers(Mock(), config_entry())
    registry.async_update_device.assert_called_once_with(
        device_id="found",
        new_identifiers={(DOMAIN, "456")},
    )
