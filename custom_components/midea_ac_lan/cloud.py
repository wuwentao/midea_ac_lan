"""Coordinators for optional Midea cloud sensors."""

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from midealan.cloud import MeijuCloud, get_midea_cloud
from midealan.devices.e3.cloud import E3CloudClient, E3DayReport
from midealan.exceptions import CloudAuthError, CloudError

from .const import CONF_ACCOUNT, CONF_SERVER, DEFAULT_CLOUD

_LOGGER = logging.getLogger(__name__)

# The cloud writes the usage report once a day; polling a few times a day
# picks a new one up shortly after it is published without stressing the
# gateway.
CLOUD_UPDATE_INTERVAL = timedelta(hours=6)
FILTER_UPDATE_INTERVAL = timedelta(hours=1)
MEIJU_CLOUD = "美的美居"


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Protocol

    class CloudReportClient[ReportT](Protocol):
        """Read an appliance-specific report using a cloud account."""

        async def async_get_report(self, appliance_id: int) -> ReportT | None:
            """Return the report or None if the server has no data."""
            ...


class MideaCloudCoordinator[ReportT](DataUpdateCoordinator[ReportT | None]):
    """Fetch an appliance report independently of its LAN connection."""

    def __init__(  # ruff: ignore[too-many-arguments]
        self,
        hass: HomeAssistant,
        client: "CloudReportClient[ReportT]",
        config_entry: ConfigEntry,
        appliance_id: int,
        device_name: str,
        *,
        update_interval: timedelta = CLOUD_UPDATE_INTERVAL,
    ) -> None:
        """Initialize the cloud usage coordinator."""
        coordinator_args = {
            "name": f"{device_name} cloud usage report",
            "update_interval": update_interval,
            "always_update": False,
        }
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 12):
            super().__init__(
                hass,
                _LOGGER,
                config_entry=config_entry,  # type: ignore[call-arg]
                **coordinator_args,
            )
        else:
            super().__init__(hass, _LOGGER, **coordinator_args)
        self._client = client
        self.appliance_id = appliance_id

    async def _async_update_data(self) -> ReportT | None:
        """Fetch and parse the usage report of the appliance.

        Returns
        -------
        ReportT | None
            The parsed report, or None when the cloud holds no report for the
            appliance yet.

        Raises
        ------
        UpdateFailed
            If the cloud could not be reached or answered with an error.

        """
        try:
            return await self._client.async_get_report(self.appliance_id)
        except CloudError as ex:
            raise UpdateFailed(str(ex)) from ex


def create_cloud_coordinator(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_id: str | int,
    device_name: str,
) -> MideaCloudCoordinator[E3DayReport] | None:
    """Create the cloud coordinator from the entry options.

    Returns
    -------
    MideaCloudCoordinator | None
        The coordinator, or None when no Midea cloud account is stored in the
        options.

    """
    options = config_entry.options
    account = options.get(CONF_ACCOUNT)
    password = options.get(CONF_PASSWORD)
    # DEFAULT_CLOUD is report-capable. Fall back to it when no server is
    # stored or the stored value is empty. An unknown stored server makes
    # E3CloudClient raise CloudError below (logged, sensors skipped); a known
    # but report-incapable one fails later in the coordinator fetch and leaves
    # the sensors unavailable.
    server = options.get(CONF_SERVER) or DEFAULT_CLOUD
    if not account or not password:
        return None
    try:
        client = E3CloudClient(
            server,
            async_get_clientsession(hass),
            account=str(account),
            password=str(password),
        )
    except CloudError as ex:
        _LOGGER.warning(
            "Unsupported Midea cloud server %s for the usage report: %s",
            server,
            ex,
        )
        return None
    return MideaCloudCoordinator(
        hass,
        client,
        config_entry,
        int(device_id),
        device_name,
    )


class MideaFilterWashTimeClient:
    """Read E1 filter wash time with the user's own Meiju session."""

    def __init__(self, cloud: MeijuCloud) -> None:
        """Initialize without starting a cloud session."""
        self._cloud = cloud
        self._authenticated = False

    async def _async_login(self) -> None:
        self._authenticated = await self._cloud.login()
        if not self._authenticated:
            raise CloudAuthError("Midea cloud login failed")

    async def async_get_report(self, appliance_id: int) -> int | None:
        """Fetch cumulative washing minutes, renewing an expired session once.

        Returns
        -------
        int | None
            Valid minutes, or None when no reading is available.

        Raises
        ------
        CloudAuthError
            If login or session renewal fails.
        CloudError
            If the installed library cannot fetch this report, or fetching fails.

        """
        # The published midea-lan release may predate this read-only query; the
        # opt-in sensor stays unavailable instead of breaking LAN entities.
        get_minutes = cast(
            "Callable[[int], Awaitable[int | None]] | None",
            getattr(self._cloud, "get_e1_filter_wash_time", None),
        )
        if get_minutes is None:
            raise CloudError("Installed midea-lan does not support filter wash time")
        for _ in range(2):
            if not self._authenticated:
                await self._async_login()
            try:
                return await get_minutes(appliance_id)
            except CloudAuthError:
                self._authenticated = False
        raise CloudAuthError("Midea cloud declined filter wash time access")


def create_filter_wash_time_coordinator(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_id: str | int,
    device_name: str,
) -> MideaCloudCoordinator[int] | None:
    """Create the opt-in filter coordinator when a personal account is set.

    Returns
    -------
    MideaCloudCoordinator[int] | None
        The coordinator, or None if the user has not entered both credentials.

    """
    account = config_entry.options.get(CONF_ACCOUNT)
    password = config_entry.options.get(CONF_PASSWORD)
    if not account or not password:
        return None
    cloud = cast(
        "MeijuCloud",
        get_midea_cloud(
            MEIJU_CLOUD,
            async_get_clientsession(hass),
            str(account),
            str(password),
        ),
    )
    return MideaCloudCoordinator(
        hass,
        MideaFilterWashTimeClient(cloud),
        config_entry,
        int(device_id),
        device_name,
        update_interval=FILTER_UPDATE_INTERVAL,
    )
