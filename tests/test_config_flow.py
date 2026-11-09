"""Tests for device configuration and options flows."""

# mypy: disable-error-code="method-assign"

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_DEVICE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SENSORS,
    CONF_SWITCHES,
    CONF_TOKEN,
    CONF_TYPE,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from midealan.device import DeviceType, ProtocolVersion

from custom_components.midea_ac_lan import config_flow
from custom_components.midea_ac_lan.config_flow import (
    MideaLanConfigFlow,
    MideaLanOptionsFlowHandler,
)
from custom_components.midea_ac_lan.const import (
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
    DEFAULT_CLOUD,
    DEVICES,
    DOMAIN,
)

DEVICE_ID = 123456


@pytest.mark.usefixtures(
    "enable_integration",
    "mock_device_selector",
    "switch_platform",
)
async def test_flow_manager_creates_manual_entry(hass: HomeAssistant) -> None:
    """Create an entry through Home Assistant's config flow manager."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={"action": "manually"},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manually"

    with (
        patch(
            "custom_components.midea_ac_lan.config_flow.discover",
            return_value={DEVICE_ID: discovered_device()},
        ),
        patch.object(MideaLanConfigFlow, "_try_connect_device", return_value=True),
        patch.object(MideaLanConfigFlow, "_save_device_config"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=manual_input(),
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Appliance"
    assert result["data"][CONF_DEVICE_ID] == DEVICE_ID
    assert result["data"][CONF_MAC] == "aabbccddeeff"


def make_flow() -> MideaLanConfigFlow:
    """Create a config flow with lightweight Home Assistant state."""
    flow = MideaLanConfigFlow()
    flow.hass = Mock()
    flow.hass.data = {}
    flow.hass.async_add_executor_job = AsyncMock()
    return flow


def discovered_device(
    *,
    protocol: ProtocolVersion = ProtocolVersion.V2,
    device_type: int = 0xAC,
) -> dict[str, object]:
    """Return a representative discovery result."""
    return {
        CONF_TYPE: device_type,
        CONF_PROTOCOL: protocol,
        CONF_IP_ADDRESS: "192.0.2.10",
        CONF_PORT: 6444,
        CONF_MODEL: "MODEL",
        CONF_MAC: "aabbccddeeff",
        CONF_SN: "00000000000000000000000000000000",
    }


def manual_input(
    *,
    protocol: ProtocolVersion = ProtocolVersion.V2,
    token: str = "",
    key: str = "",
) -> dict[str, object]:
    """Return valid manual-step input."""
    return {
        CONF_NAME: "Appliance",
        CONF_DEVICE_ID: DEVICE_ID,
        CONF_TYPE: 0xAC,
        CONF_PROTOCOL: protocol,
        CONF_IP_ADDRESS: "192.0.2.10",
        CONF_PORT: 6444,
        CONF_MODEL: "MODEL",
        CONF_SUBTYPE: 1,
        CONF_TOKEN: token,
        CONF_KEY: key,
    }


def test_init_and_cloud_name() -> None:
    """Sort supported devices and resolve cached or preset cloud names."""
    flow = make_flow()
    assert flow.supports
    assert list(flow.supports.values()) == sorted(flow.supports.values())
    assert flow._added_with_cloud_name() == DEFAULT_CLOUD
    flow.hass.data = {DOMAIN: {"login_data": {CONF_SERVER: "custom"}}}
    assert flow._added_with_cloud_name() == "custom"
    flow.hass.data[DOMAIN]["login_data"][CONF_SERVER] = ""
    assert flow._added_with_cloud_name() == DEFAULT_CLOUD


def test_save_and_load_device_config(tmp_path: Path) -> None:
    """Create storage directories, save records, and load existing or missing data."""
    flow = make_flow()
    flow.hass.config.path.side_effect = lambda *parts: str(tmp_path.joinpath(*parts))
    data = {CONF_DEVICE_ID: DEVICE_ID, CONF_NAME: "Appliance"}
    with patch("custom_components.midea_ac_lan.config_flow.save_json") as save:
        flow._save_device_config(data)
    record = tmp_path / ".storage" / DOMAIN / f"{DEVICE_ID}.json"
    assert record.parent.is_dir()
    save.assert_called_once_with(str(record), data)

    record.write_text('{"name": "Appliance"}', encoding="utf-8")
    assert flow._load_device_config(DEVICE_ID) == {"name": "Appliance"}
    assert flow._load_device_config("missing") == {}


@pytest.mark.parametrize(
    ("device", "stored", "expected"),
    [
        ({CONF_PROTOCOL: ProtocolVersion.V2}, {}, False),
        ({CONF_PROTOCOL: ProtocolVersion.V2}, {CONF_SUBTYPE: 1}, True),
        (
            {CONF_PROTOCOL: ProtocolVersion.V3},
            {CONF_SUBTYPE: 1, CONF_TOKEN: None, CONF_KEY: "key"},
            False,
        ),
        (
            {CONF_PROTOCOL: ProtocolVersion.V3},
            {CONF_SUBTYPE: 1, CONF_TOKEN: "token", CONF_KEY: None},
            False,
        ),
        (
            {CONF_PROTOCOL: ProtocolVersion.V3},
            {CONF_SUBTYPE: 1, CONF_TOKEN: "token", CONF_KEY: "key"},
            True,
        ),
    ],
)
def test_check_storage_device(
    device: dict[str, object],
    stored: dict[str, object],
    expected: bool,
) -> None:
    """Require subtype and V3 credentials in cached records."""
    assert MideaLanConfigFlow._check_storage_device(device, stored) is expected


def test_already_configured() -> None:
    """Match current entries by normalized device ID or IP address."""
    flow = make_flow()
    flow._async_current_entries = Mock(
        return_value=[
            SimpleNamespace(
                data={CONF_DEVICE_ID: "one", CONF_IP_ADDRESS: "192.0.2.1"},
            ),
            SimpleNamespace(
                data={CONF_DEVICE_ID: DEVICE_ID, CONF_IP_ADDRESS: "192.0.2.2"},
            ),
        ],
    )
    assert flow._already_configured("one", "other")
    assert flow._already_configured("other", "192.0.2.1")
    assert flow._already_configured(str(DEVICE_ID), "other")
    assert not flow._already_configured("other", "other")


@pytest.mark.parametrize(
    ("action", "target"),
    [
        ("discovery", "async_step_discovery"),
        ("manually", "async_step_manually"),
        ("cache", "async_step_cache"),
        ("list", "async_step_list"),
    ],
)
async def test_user_routes_actions(action: str, target: str) -> None:
    """Route each user action to its next flow step."""
    flow = make_flow()
    if action == "manually":
        flow.found_device = {
            CONF_DEVICE_ID: DEVICE_ID,
            CONF_CLOUD_NAME: "SmartHome",
        }
    step = AsyncMock(return_value=target)
    setattr(flow, target, step)
    assert await flow.async_step_user({"action": action}) == target
    step.assert_awaited_once_with()
    if action == "manually":
        assert flow.found_device == {}


async def test_user_and_cache_forms() -> None:
    """Show initial/cache forms and clear cached login state on confirmation."""
    flow = make_flow()
    form = await flow.async_step_user(error="problem")
    assert form["type"].value == "form"
    assert form["errors"] == {"base": "problem"}
    cache_form = await flow.async_step_cache(error="problem")
    assert cache_form["step_id"] == "cache"
    flow.hass.data = {
        DOMAIN: {
            "login_data": {CONF_SERVER: DEFAULT_CLOUD},
            "login_mode": "input",
        },
    }
    flow.async_step_user = AsyncMock(return_value="user")
    assert await flow.async_step_cache({"action": "remove"}) == "user"
    assert flow.hass.data[DOMAIN] == {}
    flow.hass.data = {}
    assert await flow.async_step_cache({"action": "remove"}) == "user"


async def test_login_form_and_input_paths() -> None:
    """Show login form, support skip-login, input-login, success, and failure."""
    flow = make_flow()
    servers = {1: DEFAULT_CLOUD, 2: "OtherCloud"}
    default_keys: dict[int, dict[str, str]] = {99: {}}
    with (
        patch.object(
            config_flow.MideaCloud,
            "get_cloud_servers",
            new_callable=AsyncMock,
            return_value=servers.copy(),
        ),
        patch.object(
            config_flow.MideaCloud,
            "get_default_keys",
            new_callable=AsyncMock,
            return_value=default_keys,
        ),
    ):
        form = await flow.async_step_login(error="bad")
        assert form["errors"] == {"base": "bad"}

        flow._check_cloud_login = AsyncMock(return_value=True)
        flow.async_step_auto = AsyncMock(return_value="auto")
        result = await flow.async_step_login(
            {CONF_SERVER: 99, CONF_ACCOUNT: "ignored", CONF_PASSWORD: "ignored"},
        )
        assert result == "auto"
        flow._check_cloud_login.assert_awaited_once_with(
            cloud_name=DEFAULT_CLOUD,
            account=flow.preset_account,
            password=flow.preset_password,
            force_login=True,
        )
        assert flow.hass.data[DOMAIN]["login_mode"] == "preset"
        assert flow.hass.data[DOMAIN]["login_data"][CONF_SERVER] == DEFAULT_CLOUD

        flow.hass.data = {}
        flow._check_cloud_login.reset_mock()
        result = await flow.async_step_login(
            {CONF_SERVER: 2, CONF_ACCOUNT: "user", CONF_PASSWORD: "password"},
        )
        assert result == "auto"
        flow._check_cloud_login.assert_awaited_once_with(
            cloud_name="OtherCloud",
            account="user",
            password="password",  # ruff: ignore[hardcoded-password-func-arg]
            force_login=True,
        )
        assert flow.hass.data[DOMAIN]["login_mode"] == "input"

        flow._check_cloud_login.return_value = False
        result = await flow.async_step_login(
            {CONF_SERVER: 2, CONF_ACCOUNT: "user", CONF_PASSWORD: "password"},
        )
        assert result["step_id"] == "login"
        assert result["errors"] == {"base": "login_failed"}


async def test_list_devices() -> None:
    """Render supported, unsupported, plain, encrypted, and empty discovery results."""
    flow = make_flow()
    supported_type = next(iter(flow.supports))
    flow.hass.async_add_executor_job.return_value = {
        1: {
            CONF_TYPE: supported_type,
            CONF_IP_ADDRESS: "192.0.2.1",
            CONF_SN: "serial",
        },
        2: {
            CONF_TYPE: 0xFFFF,
            CONF_IP_ADDRESS: "192.0.2.2",
            CONF_SN: "",
            "sn_encrypted": True,
            "support_reason": "type 0xffff uses the udp_version>=4 TLS transport",
        },
        3: {
            CONF_TYPE: 0xFFFF,
            CONF_IP_ADDRESS: "192.0.2.3",
            CONF_SN: "",
        },
    }
    result = await flow.async_step_list(error="warning")
    table = result["description_placeholders"]["table"]
    assert "serial" in table
    assert "encrypted (from cloud)" in table
    assert "YES" in table
    assert "NO" in table
    # An unsupported device surfaces midea-lan's reason verbatim when present.
    assert "udp_version>=4 TLS transport" in table
    # An unsupported device with no reason field (older midea-lan) falls back.
    assert "not yet supported" in table
    assert result["errors"] == {"base": "warning"}
    flow.hass.async_add_executor_job.return_value = {}
    result = await flow.async_step_list()
    assert result["description_placeholders"] == {"table": "Not found"}


async def test_discovery_paths() -> None:
    """Discover by auto/IP, filter configured devices, and show forms."""
    flow = make_flow()
    supported_type = next(iter(flow.supports))
    flow.hass.async_add_executor_job.return_value = {
        1: {
            **discovered_device(device_type=supported_type),
            "sn_encrypted": True,
        },
        2: discovered_device(device_type=supported_type),
    }
    flow._already_configured = Mock(side_effect=[False, True])
    flow.async_step_auto = AsyncMock(return_value="auto")
    assert await flow.async_step_discovery({CONF_IP_ADDRESS: "AUTO"}) == "auto"
    assert flow.available_device == {1: f"1 ({flow.supports[supported_type]})"}

    flow._already_configured = Mock(return_value=True)
    result = await flow.async_step_discovery({CONF_IP_ADDRESS: "192.0.2.1"})
    assert result["step_id"] == "discovery"
    assert result["errors"] == {"base": "no_devices"}
    result = await flow.async_step_discovery(error="problem")
    assert result["errors"] == {"base": "problem"}


async def test_discovery_executes_executor_callable() -> None:
    """Run library discovery through Home Assistant's executor callable."""
    flow = make_flow()
    supported_type = next(iter(flow.supports))
    flow.hass.async_add_executor_job = AsyncMock(side_effect=lambda target: target())
    flow._already_configured = Mock(return_value=False)
    flow.async_step_auto = AsyncMock(return_value="auto")
    with patch.object(
        config_flow,
        "discover",
        return_value={1: discovered_device(device_type=supported_type)},
    ) as discover_mock:
        assert await flow.async_step_discovery({CONF_IP_ADDRESS: "AUTO"}) == "auto"

    discover_mock.assert_called_once_with(list(flow.supports), ip_address=None)


async def test_cloud_login_helper() -> None:
    """Initialize/reuse cloud clients and return their login result."""
    flow = make_flow()
    session = object()
    cloud = Mock()
    cloud.login = AsyncMock(side_effect=[True, False, True])
    with (
        patch(
            "custom_components.midea_ac_lan.config_flow.async_create_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.midea_ac_lan.config_flow.get_midea_cloud",
            return_value=cloud,
        ) as factory,
    ):
        assert await flow._check_cloud_login()
        assert not await flow._check_cloud_login(
            cloud_name="custom",
            account="user",
            password="password",  # ruff: ignore[hardcoded-password-func-arg]
        )
        assert await flow._check_cloud_login(
            cloud_name="custom",
            account="user",
            password="password",  # ruff: ignore[hardcoded-password-func-arg]
            force_login=True,
        )
    assert factory.call_count == 2
    assert flow.session is session


async def test_cloud_key_helper() -> None:
    """Handle absent cloud, key filtering, connection failures, and success."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    assert await flow._check_key_from_cloud(DEVICE_ID) == {"error": "cloud_none"}

    cloud = Mock()
    cloud.get_cloud_keys = AsyncMock(
        return_value={
            1: {"token": "00", "key": "11"},
            2: {"token": "22", "key": "33"},
        },
    )
    flow.cloud = cloud
    flow.hass.async_add_executor_job.side_effect = [False, True]
    with patch.object(
        config_flow.MideaCloud,
        "get_default_keys",
        new_callable=AsyncMock,
        return_value={1: {}},
    ):
        assert await flow._check_key_from_cloud(DEVICE_ID) == {
            "token": "22",
            "key": "33",
        }

        flow.hass.async_add_executor_job.side_effect = [True]
        assert await flow._check_key_from_cloud(
            DEVICE_ID,
            default_key=False,
        ) == {"token": "22", "key": "33"}

        flow.hass.async_add_executor_job.side_effect = [False]
        assert await flow._check_key_from_cloud(
            DEVICE_ID,
            default_key=False,
        ) == {"error": "connect_error"}


def test_try_connect_device() -> None:
    """Always close the socket after successful and failed connection attempts."""
    device = Mock()
    device.connect.return_value = True
    assert MideaLanConfigFlow._try_connect_device(device)
    device.close_socket.assert_called_once_with()
    device.reset_mock()
    device.connect.side_effect = OSError("offline")
    with pytest.raises(OSError, match="offline"):
        MideaLanConfigFlow._try_connect_device(device)
    device.close_socket.assert_called_once_with()


async def test_auto_form_and_cached_record() -> None:
    """Show selection form and load complete cached device identity."""
    flow = make_flow()
    flow.available_device = {DEVICE_ID: "Device"}
    form = await flow.async_step_auto(error="problem")
    assert form["errors"] == {"base": "problem"}
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    flow.hass.async_add_executor_job.return_value = {
        CONF_NAME: "Cached",
        CONF_SUBTYPE: 2,
        CONF_TOKEN: "00",
        CONF_KEY: "11",
        CONF_SN8: "12345678",
        CONF_MANUFACTURER_CODE: "0000",
        CONF_CLOUD_NAME: "SmartHome",
    }
    flow.async_step_manually = AsyncMock(return_value="manual")
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "manual"
    assert flow.found_device[CONF_NAME] == "Cached"
    assert flow.found_device[CONF_SN8] == "12345678"


async def test_auto_login_and_v2_paths() -> None:
    """Handle missing/failed cache and continue V2 with cloud info."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device()}
    flow.hass.async_add_executor_job.return_value = {}
    flow.async_step_login = AsyncMock(return_value="login")
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "login"

    flow.hass.data = {
        DOMAIN: {
            "login_data": {
                CONF_SERVER: DEFAULT_CLOUD,
                CONF_ACCOUNT: "user",
                CONF_PASSWORD: "password",
            },
            "login_mode": "input",
        },
    }
    flow._check_cloud_login = AsyncMock(return_value=False)
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "login"
    assert flow.hass.data[DOMAIN] == {}

    cloud = Mock()
    cloud.get_device_info = AsyncMock(
        return_value={
            "name": "Cloud name",
            "model_number": 3,
            "sn8": "12345678",
            "manufacturer_code": "0000",
        },
    )
    flow.cloud = cloud
    flow.hass.data = {
        DOMAIN: {
            "login_data": {
                CONF_SERVER: DEFAULT_CLOUD,
                CONF_ACCOUNT: "user",
                CONF_PASSWORD: "password",
            },
            "login_mode": "input",
        },
    }
    flow.async_step_manually = AsyncMock(return_value="manual")
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "manual"
    assert flow.found_device[CONF_NAME] == "Cloud name"
    cloud.get_device_info.return_value = None
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "manual"


@pytest.mark.parametrize(
    ("mode", "login_result", "phase_two_keys", "expected_error"),
    [
        ("preset", True, None, "can't get valid token from Midea server"),
        ("input", False, None, "Perset account login failed!"),
        (
            "input",
            True,
            {},
            f"Can't get available token from Midea server for device {DEVICE_ID}",
        ),
    ],
)
async def test_auto_v3_failure_paths(
    mode: str,
    login_result: bool,
    phase_two_keys: dict[str, str] | None,
    expected_error: str,
) -> None:
    """Report preset, fallback-login, and fallback-key failures."""
    flow = make_flow()
    flow.available_device = {DEVICE_ID: "Device"}
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    flow.hass.async_add_executor_job.return_value = {}
    flow.hass.data = {
        DOMAIN: {
            "login_data": {
                CONF_SERVER: DEFAULT_CLOUD,
                CONF_ACCOUNT: "user",
                CONF_PASSWORD: "password",
            },
            "login_mode": mode,
        },
    }
    flow.cloud = Mock()
    flow.cloud.get_device_info = AsyncMock(return_value=None)
    keys = [{"error": "missing"}]
    if phase_two_keys is not None:
        keys.append(phase_two_keys)
    flow._check_key_from_cloud = AsyncMock(side_effect=keys)
    flow._check_cloud_login = AsyncMock(return_value=login_result)
    result = await flow.async_step_auto({CONF_DEVICE: DEVICE_ID})
    assert result["step_id"] == "auto"
    assert result["errors"] == {"base": expected_error}


async def test_auto_v3_key_success_paths() -> None:
    """Continue after first-phase and fallback-phase Token/Key success."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    flow.hass.async_add_executor_job.return_value = {}
    flow.hass.data = {
        DOMAIN: {
            "login_data": {
                CONF_SERVER: DEFAULT_CLOUD,
                CONF_ACCOUNT: "user",
                CONF_PASSWORD: "password",
            },
            "login_mode": "input",
        },
    }
    flow.cloud = Mock()
    flow.cloud.get_device_info = AsyncMock(return_value=None)
    flow.async_step_manually = AsyncMock(return_value="manual")
    flow._check_key_from_cloud = AsyncMock(return_value={"token": "00", "key": "11"})
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "manual"
    assert flow.found_device[CONF_TOKEN] == "00"

    flow._check_key_from_cloud = AsyncMock(
        side_effect=[{"error": "missing"}, {"token": "22", "key": "33"}],
    )
    flow._check_cloud_login = AsyncMock(return_value=True)
    assert await flow.async_step_auto({CONF_DEVICE: DEVICE_ID}) == "manual"
    assert flow.found_device[CONF_KEY] == "33"
    flow._check_cloud_login.assert_awaited_once_with(force_login=True)
    assert flow._check_key_from_cloud.await_args_list[-1].kwargs == {
        "default_key": False,
    }


async def test_manual_form_and_validation_errors() -> None:
    """Show defaults and report Token, discovery, ID, IP, and protocol errors."""
    flow = make_flow()
    flow.found_device = {}
    form = await flow.async_step_manually(error="problem")
    assert form["errors"] == {"base": "problem"}
    flow.found_device = manual_input()
    assert (await flow.async_step_manually())["step_id"] == "manually"

    invalid = manual_input(
        token="invalid",  # ruff: ignore[hardcoded-password-func-arg]
        key="invalid",
    )
    assert (await flow.async_step_manually(invalid))["errors"] == {
        "base": "invalid_token",
    }

    valid = manual_input()
    flow.devices = {}
    flow.hass.async_add_executor_job.return_value = {}
    assert (await flow.async_step_manually(valid.copy()))["errors"] == {
        "base": "invalid_device_ip",
    }
    flow.hass.async_add_executor_job.return_value = {
        999: discovered_device(),
    }
    assert (
        "device_id MUST be 999"
        in (await flow.async_step_manually(valid.copy()))["errors"]["base"]
    )

    flow.devices = {}
    flow.hass.async_add_executor_job.side_effect = [
        {DEVICE_ID: discovered_device()},
        False,
    ]
    assert (await flow.async_step_manually(valid.copy()))["errors"] == {
        "base": "Device auth failed with input config",
    }
    flow.hass.async_add_executor_job.side_effect = None

    flow.devices = {DEVICE_ID: discovered_device()}
    wrong_ip = valid.copy()
    wrong_ip[CONF_IP_ADDRESS] = "192.0.2.99"
    assert (
        "ip_address MUST be"
        in (await flow.async_step_manually(wrong_ip))["errors"]["base"]
    )
    wrong_protocol = valid.copy()
    wrong_protocol[CONF_PROTOCOL] = ProtocolVersion.V1
    assert (
        "protocol MUST be"
        in (await flow.async_step_manually(wrong_protocol))["errors"]["base"]
    )


@pytest.mark.parametrize(
    ("login", "keys", "expected_error"),
    [
        (False, {}, "Perset account login failed!"),
        (True, {}, f"Can't get a valid token from Midea server for device {DEVICE_ID}"),
    ],
)
async def test_manual_v3_credential_failures(
    login: bool,
    keys: dict[str, str],
    expected_error: str,
) -> None:
    """Report preset login and missing cloud Token/Key failures."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    flow._check_cloud_login = AsyncMock(return_value=login)
    flow._check_key_from_cloud = AsyncMock(return_value=keys)
    result = await flow.async_step_manually(
        manual_input(protocol=ProtocolVersion.V3),
    )
    assert result["errors"] == {"base": expected_error}


async def test_manual_connection_success_and_failure() -> None:
    """Fill cloud keys, preserve identity, verify connection, save, and create entry."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device(protocol=ProtocolVersion.V3)}
    flow.found_device = {
        CONF_SN8: "12345678",
        CONF_MANUFACTURER_CODE: "0000",
        CONF_CLOUD_NAME: "SmartHome",
    }
    flow._check_cloud_login = AsyncMock(return_value=True)
    flow._check_key_from_cloud = AsyncMock(return_value={"token": "00", "key": "11"})
    flow.hass.async_add_executor_job.side_effect = [True, None]
    result = await flow.async_step_manually(
        manual_input(protocol=ProtocolVersion.V3),
    )
    assert result["type"].value == "create_entry"
    assert result["data"][CONF_TOKEN] == "00"
    assert result["data"][CONF_CLOUD_NAME] == "SmartHome"
    assert result["data"][CONF_SN8] == "12345678"
    flow.hass.async_add_executor_job.assert_any_await(
        flow._save_device_config,
        result["data"],
    )

    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device()}
    flow.hass.async_add_executor_job.return_value = False
    result = await flow.async_step_manually(manual_input())
    assert result["errors"] == {"base": "Device auth failed with input config"}


async def test_manual_cloud_name_fallback() -> None:
    """Persist the active cloud when no identity was carried from auto discovery."""
    flow = make_flow()
    flow.devices = {DEVICE_ID: discovered_device()}
    flow.hass.data = {DOMAIN: {"login_data": {CONF_SERVER: "custom"}}}
    flow.hass.async_add_executor_job.side_effect = [True, None]
    result = await flow.async_step_manually(manual_input())
    assert result["data"][CONF_CLOUD_NAME] == "custom"


def test_options_flow_factory_and_defaults() -> None:
    """Create an options handler and default missing device types to AC."""
    entry = SimpleNamespace(data={CONF_TYPE: None}, options={})
    handler = MideaLanConfigFlow.async_get_options_flow(entry)
    assert isinstance(handler, MideaLanOptionsFlowHandler)
    assert handler._device_type == 0xAC


async def test_options_flow_abort_and_save() -> None:
    """Abort account entries and save submitted device options."""
    account = MideaLanOptionsFlowHandler(
        SimpleNamespace(data={CONF_TYPE: CONF_ACCOUNT}, options={}),
    )
    result = await account.async_step_init()
    assert result["reason"] == "account_option"
    handler = MideaLanOptionsFlowHandler(
        SimpleNamespace(data={CONF_TYPE: 0xAC}, options={}),
    )
    result = await handler.async_step_init({CONF_REFRESH_INTERVAL: 30})
    assert result["data"] == {CONF_REFRESH_INTERVAL: 30}


async def test_options_flow_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    """Add filtered entity, cloud, and customize option fields."""
    entities = {
        "sensor": {"type": Platform.SENSOR, "name": "Sensor"},
        "binary": {"type": Platform.BINARY_SENSOR, "name": "Binary"},
        "switch": {"type": Platform.SWITCH, "name": "Switch"},
        "default_control": {
            "type": Platform.SWITCH,
            "name": "Default",
            "default": True,
        },
        "unsupported": {
            "type": Platform.SENSOR,
            "name": "Unsupported",
            "models": ["OTHER"],
        },
        "required_missing": {
            "type": Platform.SENSOR,
            "name": "Missing",
            "required_attribute": "missing",
        },
        "required_selected": {
            "type": Platform.SENSOR,
            "name": "Selected",
            "required_attribute": "missing",
        },
        "required_present": {
            "type": Platform.SWITCH,
            "name": "Present",
            "required_attribute": "capability",
        },
    }
    monkeypatch.setitem(
        config_flow.MIDEA_DEVICES,
        DeviceType.E3,
        {"name": "E3", "entities": entities},
    )
    entry = SimpleNamespace(
        data={
            CONF_TYPE: DeviceType.E3,
            CONF_DEVICE_ID: DEVICE_ID,
            CONF_MODEL: "MODEL",
            CONF_SUBTYPE: 1,
            CONF_IP_ADDRESS: "192.0.2.1",
        },
        options={
            CONF_IP_ADDRESS: "192.0.2.9",
            CONF_SENSORS: ["sensor", "required_selected", "stale"],
            CONF_SWITCHES: ["switch", "stale"],
            CONF_REFRESH_INTERVAL: 15,
            CONF_CUSTOMIZE: "{}",
        },
    )
    device = Mock()
    device.attributes = {"capability": True}
    device.get_attribute.side_effect = device.attributes.get
    handler = MideaLanOptionsFlowHandler(entry)
    handler.hass = SimpleNamespace(
        data={DOMAIN: {DEVICES: {DEVICE_ID: device}}},
    )
    result = await handler.async_step_init()
    schema = result["data_schema"]
    validated = schema(
        {
            CONF_IP_ADDRESS: "192.0.2.2",
            CONF_REFRESH_INTERVAL: 20,
            CONF_SENSORS: ["sensor", "required_selected"],
            CONF_SWITCHES: ["switch", "required_present"],
            CONF_ACCOUNT: "user",
            CONF_PASSWORD: "password",
            CONF_SERVER: DEFAULT_CLOUD,
            CONF_CUSTOMIZE: "{}",
        },
    )
    assert validated[CONF_REFRESH_INTERVAL] == 20


async def test_options_flow_without_optional_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build a minimal schema when no extra entities or loaded device exist."""
    monkeypatch.setitem(
        config_flow.MIDEA_DEVICES,
        1,
        {
            "name": "Device",
            "entities": {
                "required": {
                    "type": Platform.SENSOR,
                    "required_attribute": "missing",
                },
            },
        },
    )
    entry = SimpleNamespace(
        data={CONF_TYPE: 1, CONF_DEVICE_ID: None, CONF_MODEL: "MODEL"},
        options={},
    )
    handler = MideaLanOptionsFlowHandler(entry)
    handler.hass = SimpleNamespace(data={})
    result = await handler.async_step_init()
    assert result["step_id"] == "init"
