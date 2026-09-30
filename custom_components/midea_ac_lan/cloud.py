"""Midea cloud coordinator.

Currently fetches the E3 usage report; keep this module cloud-generic so more
cloud-backed features can share it without adding another file.
"""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from midealan.devices.e3.cloud import E3CloudClient, E3DayReport
from midealan.exceptions import CloudError

from .const import CONF_ACCOUNT, CONF_SERVER, DEFAULT_REPORT_CLOUD, REPORT_CLOUDS

_LOGGER = logging.getLogger(__name__)

# The cloud writes the usage report once a day; polling a few times a day
# picks a new one up shortly after it is published without stressing the
# gateway.
CLOUD_UPDATE_INTERVAL = timedelta(hours=6)


class MideaCloudCoordinator(DataUpdateCoordinator[E3DayReport | None]):
    """Fetch the Midea cloud usage report of an appliance."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: E3CloudClient,
        appliance_id: int,
        device_name: str,
    ) -> None:
        """Initialize the cloud usage coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{device_name} cloud usage report",
            update_interval=CLOUD_UPDATE_INTERVAL,
            always_update=False,
        )
        self._client = client
        self.appliance_id = appliance_id

    async def _async_update_data(self) -> E3DayReport | None:
        """Fetch and parse the usage report of the appliance.

        Returns
        -------
        E3DayReport | None
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
) -> MideaCloudCoordinator | None:
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
    # Fall back to a report-capable cloud when no server is stored or the
    # stored one cannot serve the usage report (e.g. an older entry saved with
    # DEFAULT_CLOUD); otherwise the report request raises CloudError and the
    # sensors would stay permanently unavailable.
    server = options.get(CONF_SERVER, DEFAULT_REPORT_CLOUD)
    if server not in REPORT_CLOUDS:
        server = DEFAULT_REPORT_CLOUD
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
    return MideaCloudCoordinator(hass, client, int(device_id), device_name)
