"""Tests for the Midea cloud usage coordinator."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers.update_coordinator import UpdateFailed
from midealan.exceptions import CloudError

from custom_components.midea_ac_lan.cloud import (
    MideaCloudCoordinator,
    create_cloud_coordinator,
)
from custom_components.midea_ac_lan.const import (
    CONF_ACCOUNT,
    CONF_SERVER,
    DEFAULT_CLOUD,
)


async def test_coordinator_update_success_and_error() -> None:
    """Return reports and translate library cloud failures for Home Assistant."""
    hass = Mock()
    client = Mock()
    report = object()
    client.async_get_report = AsyncMock(return_value=report)
    coordinator = MideaCloudCoordinator(
        hass,
        client,
        Mock(),
        123,
        "Water heater",
    )

    assert coordinator.appliance_id == 123
    assert await coordinator._async_update_data() is report
    client.async_get_report.assert_awaited_once_with(123)

    client.async_get_report.side_effect = CloudError("offline")
    with pytest.raises(UpdateFailed, match="offline"):
        await coordinator._async_update_data()


@pytest.mark.parametrize(
    ("version", "expects_config_entry"),
    [((2024, 4), False), ((2024, 12), True)],
)
def test_coordinator_version_specific_config_entry(
    version: tuple[int, int],
    expects_config_entry: bool,
) -> None:
    """Pass config_entry only to Home Assistant versions that support it."""
    entry = Mock()
    with (
        patch("custom_components.midea_ac_lan.cloud.MAJOR_VERSION", version[0]),
        patch("custom_components.midea_ac_lan.cloud.MINOR_VERSION", version[1]),
        patch(
            "custom_components.midea_ac_lan.cloud.DataUpdateCoordinator.__init__",
            return_value=None,
        ) as coordinator_init,
    ):
        coordinator = MideaCloudCoordinator(Mock(), Mock(), entry, 123, "Device")

    assert coordinator.appliance_id == 123
    if expects_config_entry:
        assert coordinator_init.call_args.kwargs["config_entry"] is entry
    else:
        assert "config_entry" not in coordinator_init.call_args.kwargs


@pytest.mark.parametrize(
    "options",
    [
        {},
        {CONF_ACCOUNT: "user"},
        {CONF_PASSWORD: "secret"},
        {CONF_ACCOUNT: "", CONF_PASSWORD: "secret"},
    ],
)
def test_create_coordinator_requires_credentials(options: dict[str, str]) -> None:
    """Skip cloud features unless both credentials are stored."""
    entry = Mock(options=options)
    assert create_cloud_coordinator(Mock(), entry, 1, "Device") is None


@pytest.mark.parametrize(
    ("stored_server", "expected_server"),
    [(None, DEFAULT_CLOUD), ("", DEFAULT_CLOUD), ("custom", "custom")],
)
def test_create_coordinator(
    stored_server: str | None,
    expected_server: str,
) -> None:
    """Create a coordinator with the selected server and converted device ID."""
    options = {CONF_ACCOUNT: "user", CONF_PASSWORD: "secret"}
    if stored_server is not None:
        options[CONF_SERVER] = stored_server
    entry = Mock(options=options)
    hass = Mock()
    session = object()
    client = Mock()
    with (
        patch(
            "custom_components.midea_ac_lan.cloud.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.midea_ac_lan.cloud.E3CloudClient",
            return_value=client,
        ) as client_class,
    ):
        coordinator = create_cloud_coordinator(hass, entry, "42", "Device")

    client_class.assert_called_once_with(
        expected_server,
        session,
        account="user",
        password="secret",  # ruff: ignore[hardcoded-password-func-arg] - test value
    )
    assert coordinator is not None
    assert coordinator.appliance_id == 42


def test_create_coordinator_rejects_unsupported_server() -> None:
    """Skip usage sensors when the library rejects the stored server."""
    entry = SimpleNamespace(
        options={
            CONF_ACCOUNT: "user",
            CONF_PASSWORD: "secret",
            CONF_SERVER: "unsupported",
        },
    )
    with (
        patch("custom_components.midea_ac_lan.cloud.async_get_clientsession"),
        patch(
            "custom_components.midea_ac_lan.cloud.E3CloudClient",
            side_effect=CloudError("unsupported"),
        ),
    ):
        assert create_cloud_coordinator(Mock(), entry, 1, "Device") is None
