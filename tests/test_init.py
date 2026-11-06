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
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
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
    CONF_SERVER,
    CONF_SN,
    CONF_SN8,
    CONF_SUBTYPE,
    CONF_TLS,
    DEVICES,
    DOMAIN,
)


class Attribute(StrEnum):
    """Non-string registry key used to cover enum-backed attributes."""

    POWER = "power"


def test_close_device_success_and_expected_errors() -> None:
    """Close normally and absorb connection cleanup failures."""
    device = Mock()
    midea_ac_lan._close_device(device)
    device.close.assert_called_once_with()
    for error in (OSError("socket"), ConnectionError("closed"), AttributeError("old")):
        device.close.reset_mock(side_effect=True)
        device.close.side_effect = error
        midea_ac_lan._close_device(device)


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
    assert await midea_ac_lan.async_setup(hass, {})

    assert hass.services.async_register.call_count == 2
    set_attribute = hass.services.async_register.call_args_list[0].args[2]
    send_command = hass.services.async_register.call_args_list[1].args[2]
    device = Mock()
    device.device_type = 1
    hass.data[DOMAIN][DEVICES] = {7: device}

    set_attribute(
        SimpleNamespace(data={"device_id": 7, "attribute": "mapped", "value": 3}),
    )
    device.set_attribute.assert_called_once_with(attr="target", value=3)
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
    device.open.assert_called_once_with()
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
    hass.async_add_executor_job.assert_awaited_once_with(
        midea_ac_lan._close_device,
        device,
    )
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
    hass.async_add_executor_job.assert_awaited_once_with(
        midea_ac_lan._close_device,
        device,
    )


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
    hass.config_entries.async_update_entry.assert_called_once_with(
        entry,
        minor_version=2,
    )

    hass.reset_mock()
    with patch(
        "custom_components.midea_ac_lan._async_backfill_mac_and_sn",
        new_callable=AsyncMock,
        return_value=False,
    ):
        assert await midea_ac_lan.async_migrate_entry(hass, entry)
    hass.config_entries.async_update_entry.assert_not_called()


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


def tls_account(**overrides: object) -> dict[str, object]:
    """Build a stored account.json mapping carrying the TLS cloud credentials."""
    account: dict[str, object] = {
        CONF_ACCOUNT: "user@example.com",
        CONF_PASSWORD: "secret",
        CONF_SERVER: "SmartHome",
    }
    account.update(overrides)
    return account


def hass_with_account(account: dict[str, object]) -> Mock:
    """Build a hass mock whose executor returns the stored TLS account."""
    hass = Mock()
    hass.async_add_executor_job = AsyncMock(return_value=account)
    return hass


def test_load_tls_account_missing_file() -> None:
    """Return an empty mapping when account.json does not exist."""
    hass = Mock()
    hass.config.path.return_value = "/does/not/exist/account.json"
    with patch.object(midea_ac_lan.Path, "exists", return_value=False):
        assert midea_ac_lan._load_tls_account(hass) == {}


def test_load_tls_account_reads_json() -> None:
    """Return the stored account mapping when account.json exists."""
    hass = Mock()
    hass.config.path.return_value = "/config/.storage/midea_ac_lan/account.json"
    account = tls_account()
    with (
        patch.object(midea_ac_lan.Path, "exists", return_value=True),
        patch.object(midea_ac_lan, "load_json", return_value=account) as load,
    ):
        assert midea_ac_lan._load_tls_account(hass) == account
    load.assert_called_once()


@pytest.mark.parametrize(
    "account",
    [
        {CONF_ACCOUNT: "", CONF_PASSWORD: "secret", CONF_SERVER: "SmartHome"},
        {CONF_ACCOUNT: "user@example.com", CONF_PASSWORD: "", CONF_SERVER: "SmartHome"},
        {},
    ],
)
async def test_provision_tls_cert_missing_credentials(
    account: dict[str, object],
) -> None:
    """Return None when account.json has no stored Midea account."""
    hass = hass_with_account(account)
    entry = config_entry(data=entry_data(**{CONF_TLS: True}))
    assert await midea_ac_lan._provision_tls_cert(hass, entry) is None


async def test_provision_tls_cert_login_failure() -> None:
    """Return None when the cloud login fails."""
    hass = hass_with_account(tls_account())
    entry = config_entry(data=entry_data(**{CONF_TLS: True}))
    cloud = Mock()
    cloud.login = AsyncMock(return_value=False)
    cloud.apply_cert = AsyncMock()
    with (
        patch.object(midea_ac_lan, "get_midea_cloud", return_value=cloud),
        patch.object(midea_ac_lan, "async_get_clientsession"),
    ):
        assert await midea_ac_lan._provision_tls_cert(hass, entry) is None
    cloud.apply_cert.assert_not_awaited()


async def test_provision_tls_cert_success_defaults_server() -> None:
    """Log in and return the bundle, defaulting the server when unset."""
    hass = hass_with_account(tls_account(**{CONF_SERVER: ""}))
    entry = config_entry(data=entry_data(**{CONF_TLS: True}))
    bundle = Mock()
    cloud = Mock()
    cloud.login = AsyncMock(return_value=True)
    cloud.apply_cert = AsyncMock(return_value=bundle)
    with (
        patch.object(
            midea_ac_lan,
            "get_midea_cloud",
            return_value=cloud,
        ) as get_cloud,
        patch.object(midea_ac_lan, "async_get_clientsession"),
    ):
        assert await midea_ac_lan._provision_tls_cert(hass, entry) is bundle
    assert get_cloud.call_args.args[0] == midea_ac_lan.DEFAULT_CLOUD


async def test_async_setup_entry_tls_provision_failure() -> None:
    """Reject a TLS entry when certificate provisioning fails."""
    hass, _, _ = setup_hass(None)
    entry = config_entry(
        data=entry_data(**{CONF_TLS: True, CONF_PROTOCOL: ProtocolVersion.V3}),
    )
    with patch.object(
        midea_ac_lan,
        "_provision_tls_cert",
        new_callable=AsyncMock,
        return_value=None,
    ):
        assert not await midea_ac_lan.async_setup_entry(hass, entry)
    hass.async_add_import_executor_job.assert_not_awaited()


async def test_async_setup_entry_tls_success_threads_cert_bundle() -> None:
    """Provision a certificate and pass the bundle to device_selector."""
    device = Mock()
    device.device_type = 1
    device.device_id = 42
    device.model = "MODEL"
    device.subtype = 1
    hass, _, _ = setup_hass(device)
    bundle = Mock()
    entry = config_entry(
        data=entry_data(**{CONF_TLS: True, CONF_PROTOCOL: ProtocolVersion.V3}),
    )
    with (
        patch.object(
            midea_ac_lan,
            "_provision_tls_cert",
            new_callable=AsyncMock,
            return_value=bundle,
        ),
        patch.object(midea_ac_lan, "MIDEA_DEVICES", {1: {"entities": {}}}),
        patch.object(midea_ac_lan, "_remove_unsupported_entities"),
    ):
        assert await midea_ac_lan.async_setup_entry(hass, entry)
    # The certificate bundle is the final positional argument to device_selector.
    assert hass.async_add_import_executor_job.await_args.args[-1] is bundle
