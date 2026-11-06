"""Tests for the TLS (udp_version >= 4) device path in the config flow.

These cover the certificate-provisioning branch added for udp_version >= 4
devices, which authenticate with an app certificate instead of a token/key.
Kept in a dedicated module so it does not collide with the broader
``test_config_flow.py`` coverage suite.
"""

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.const import (
    CONF_DEVICE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_TOKEN,
    CONF_TYPE,
)
from midealan.device import ProtocolVersion

from custom_components.midea_ac_lan.config_flow import MideaLanConfigFlow
from custom_components.midea_ac_lan.const import (
    CONF_ACCOUNT,
    CONF_CLOUD_NAME,
    CONF_KEY,
    CONF_MODEL,
    CONF_SERVER,
    CONF_SUBTYPE,
    CONF_TLS,
    DOMAIN,
)

_DEVICE_ID = 42


def _tls_device() -> dict[str, Any]:
    """Return a discovered TLS device dict (empty SN, sn_encrypted flagged)."""
    return {
        CONF_TYPE: 0xE3,
        CONF_PROTOCOL: ProtocolVersion.V3,
        CONF_IP_ADDRESS: "192.0.2.10",
        CONF_PORT: 6444,
        CONF_MODEL: "JSLQ27M10SPlus",
        "mac": "aabbccddeeff",
        "sn": "",
        "sn_encrypted": True,
    }


def _flow() -> MideaLanConfigFlow:
    """Build a config flow with cloud login state prepared for a TLS add."""
    flow = MideaLanConfigFlow()
    flow.hass = Mock()
    flow.hass.data = {
        DOMAIN: {
            "login_data": {
                CONF_ACCOUNT: "user@example.com",
                CONF_PASSWORD: "secret",
                CONF_SERVER: "SmartHome",
            },
        },
    }
    # Run executor jobs inline so _try_connect_device / _save_device_config run.
    flow.hass.async_add_executor_job = AsyncMock(
        side_effect=lambda func, *args: func(*args),
    )
    flow.devices = {_DEVICE_ID: _tls_device()}
    flow.found_device = {CONF_SUBTYPE: 3}
    flow.supports = {0xE3: "E3 Device"}
    return flow


async def test_tls_device_no_cloud_returns_to_auto() -> None:
    """Fall back to the auto step when cloud login is missing."""
    flow = _flow()
    flow.cloud = None
    with patch.object(
        flow,
        "async_step_auto",
        new_callable=AsyncMock,
        return_value="auto",
    ) as auto:
        assert await flow._async_add_tls_device(_DEVICE_ID, _tls_device()) == "auto"
    assert auto.await_args is not None
    assert "Cloud login is required" in auto.await_args.kwargs["error"]


async def test_tls_device_apply_cert_none_returns_to_auto() -> None:
    """Fall back to the auto step when the cloud cannot provision a cert."""
    flow = _flow()
    flow.cloud = Mock()
    flow.cloud.apply_cert = AsyncMock(return_value=None)
    with patch.object(
        flow,
        "async_step_auto",
        new_callable=AsyncMock,
        return_value="auto",
    ) as auto:
        assert await flow._async_add_tls_device(_DEVICE_ID, _tls_device()) == "auto"
    assert auto.await_args is not None
    assert "personal Midea account" in auto.await_args.kwargs["error"]


async def test_tls_device_connect_failure_returns_to_auto() -> None:
    """Fall back to the auto step when the connection test fails."""
    flow = _flow()
    flow.cloud = Mock()
    flow.cloud.apply_cert = AsyncMock(return_value=Mock())
    with (
        patch.object(MideaLanConfigFlow, "_try_connect_device", return_value=False),
        patch.object(
            flow,
            "async_step_auto",
            new_callable=AsyncMock,
            return_value="auto",
        ) as auto,
    ):
        assert await flow._async_add_tls_device(_DEVICE_ID, _tls_device()) == "auto"
    assert auto.await_args is not None
    error = auto.await_args.kwargs["error"]
    assert f"Can't connect to TLS device {_DEVICE_ID}" in error


async def test_tls_device_success_creates_entry() -> None:
    """Create a TLS-flagged entry and save the cloud account to account.json."""
    flow = _flow()
    flow.cloud = Mock()
    bundle = Mock()
    flow.cloud.apply_cert = AsyncMock(return_value=bundle)

    with (
        patch.object(MideaLanConfigFlow, "_try_connect_device", return_value=True),
        patch.object(flow, "_save_device_config") as save,
        patch.object(flow, "_save_tls_account") as save_account,
        patch.object(
            flow,
            "async_create_entry",
            side_effect=lambda **kwargs: kwargs,
        ) as create_entry,
    ):
        result = await flow._async_add_tls_device(_DEVICE_ID, _tls_device())

    created = create_entry.call_args.kwargs
    assert result == created
    data = created["data"]
    assert data[CONF_TLS] is True
    assert data[CONF_TOKEN] == ""
    assert data[CONF_KEY] == ""
    assert data[CONF_DEVICE_ID] == _DEVICE_ID
    assert data[CONF_CLOUD_NAME] == "SmartHome"
    # Credentials are saved to account.json, never to the config entry.
    assert "options" not in created
    save.assert_called_once()
    save_account.assert_called_once()
    account = save_account.call_args.args[0]
    assert account[CONF_ACCOUNT] == "user@example.com"
    assert account[CONF_PASSWORD] == "secret"
    assert account[CONF_SERVER] == "SmartHome"


async def test_tls_device_success_default_name() -> None:
    """Use the supported-device label when the cloud returns no name."""
    flow = _flow()
    flow.found_device = {}
    flow.cloud = Mock()
    flow.cloud.apply_cert = AsyncMock(return_value=Mock())
    with (
        patch.object(MideaLanConfigFlow, "_try_connect_device", return_value=True),
        patch.object(flow, "_save_device_config"),
        patch.object(flow, "_save_tls_account"),
        patch.object(
            flow,
            "async_create_entry",
            side_effect=lambda **kwargs: kwargs,
        ),
    ):
        result = await flow._async_add_tls_device(_DEVICE_ID, _tls_device())
    assert result["title"] == "E3 Device"
    assert result["data"][CONF_NAME] == "E3 Device"
    assert result["data"][CONF_SUBTYPE] == 0


def test_save_tls_account_writes_json(tmp_path: Path) -> None:
    """Persist the shared cloud account to account.json under STORAGE_PATH."""
    flow = _flow()
    flow.hass.config.path.side_effect = lambda *parts: str(tmp_path.joinpath(*parts))
    account = {
        CONF_ACCOUNT: "user@example.com",
        CONF_PASSWORD: "secret",
        CONF_SERVER: "SmartHome",
    }
    with patch(
        "custom_components.midea_ac_lan.config_flow.save_json",
    ) as save_json:
        flow._save_tls_account(account)
    save_json.assert_called_once()
    saved_path, saved_account = save_json.call_args.args
    assert saved_path.endswith("account.json")
    assert saved_account == account


async def test_auto_step_routes_tls_device() -> None:
    """async_step_auto dispatches a discovered TLS device to the TLS add path."""
    flow = _flow()
    flow.cloud = Mock()
    flow.cloud.get_device_info = AsyncMock(return_value=None)
    flow._check_cloud_login = AsyncMock(return_value=True)  # type: ignore[method-assign]
    with (
        patch.object(
            flow,
            "_load_device_config",
            return_value={},
        ),
        patch.object(
            flow,
            "_async_add_tls_device",
            new_callable=AsyncMock,
            return_value="tls",
        ) as tls_add,
    ):
        result = await flow.async_step_auto({CONF_DEVICE: _DEVICE_ID})
    assert result == "tls"
    tls_add.assert_awaited_once()
    assert tls_add.await_args is not None
    assert tls_add.await_args.args[0] == _DEVICE_ID
