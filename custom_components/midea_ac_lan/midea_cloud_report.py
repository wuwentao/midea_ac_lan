"""Midea cloud usage report for E3 gas water heaters.

The E3 local protocol does not report water or gas consumption; those values
only exist in the Midea cloud. The official app requests them with the
``dayReportV2`` message::

    POST {api_url}?alias=/cfhrs/e3/v1/api
    {"msg": "dayReportV2", "params": {"applianceId": "<appliance id>"}}

``api_url`` is the per-cloud proxy base (``midealan.cloud.SUPPORTED_CLOUDS``)
and authentication is the app user ``accessToken`` (the device LAN ``token``
from the saved device json is NOT accepted: the gateway answers 40002), sent as
the ``accessToken`` HTTP header. The response carries water (litres), gas
(cubic metres) and hot-water runtime (minutes) for the last 7 and 31 days and
for the last 12 calendar months.

Credentials come from the options dialog or the locally saved device json: a
pre-obtained ``access_token`` is used directly, otherwise the account is used
to log in and refresh the token when it expires.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, cast

from aiohttp import ClientError, ClientSession, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from midealan.cloud import SUPPORTED_CLOUDS, MeijuCloud, SmartHomeCloud

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

REPORT_ALIAS = "/cfhrs/e3/v1/api"
DAY_REPORT_MESSAGE = "dayReportV2"
REQUEST_TIMEOUT = ClientTimeout(total=20)
UPDATE_INTERVAL = timedelta(hours=1)
DAILY_SERIES_LENGTH = 31
WEEK_SERIES_LENGTH = 7
MONTHLY_SERIES_LENGTH = 12
# The gateway answers these codes when the access token is missing, rejected or
# not a user token; the caller then logs in again instead of treating it as a
# transient failure.
AUTH_ERROR_CODES = frozenset({40001, 40002, 44001})
# A token issued by a fresh login is rejected for a couple of seconds until the
# gateway propagates it, so an auth failure is retried once after this delay.
AUTH_RETRY_DELAY = 3.0


class MideaCloudReportError(Exception):
    """Midea cloud usage report request failed."""


class MideaCloudAuthError(MideaCloudReportError):
    """Midea cloud credentials are missing, invalid or expired."""


@dataclass(frozen=True, slots=True)
class CloudReportCredentials:
    """Credentials used to request the E3 usage report.

    Either an ``access_token`` (used as is) or an ``account``/``password`` pair
    (used to log in and refresh the token) must be provided.
    """

    cloud_name: str
    access_token: str = ""
    account: str = ""
    password: str = ""

    @property
    def has_login(self) -> bool:
        """Whether account credentials allow a re-login."""
        return bool(self.account and self.password)


def _report_url(cloud_name: str) -> str:
    """Return the usage report URL for a cloud.

    Returns
    -------
    str
        The full proxy URL including the report alias.

    Raises
    ------
    MideaCloudReportError
        If the cloud is unknown or has no proxy with alias support.

    """
    cloud_data = SUPPORTED_CLOUDS.get(cloud_name)
    if cloud_data is None:
        msg = f"Unsupported cloud: {cloud_name}"
        raise MideaCloudReportError(msg)
    api_url = cloud_data.get("api_url", "")
    if "alias=" not in api_url:
        msg = f"Cloud {cloud_name} does not provide usage reports"
        raise MideaCloudReportError(msg)
    return f"{api_url}{REPORT_ALIAS}"


def _raise_error(code: int, message: str) -> None:
    """Raise the matching report error for a gateway error payload.

    Raises
    ------
    MideaCloudAuthError
        If the gateway rejected the access token.
    MideaCloudReportError
        For any other gateway error.

    """
    if code in AUTH_ERROR_CODES:
        msg = f"{code}: {message}"
        raise MideaCloudAuthError(msg)
    msg = f"{code}: {message}"
    raise MideaCloudReportError(msg)


async def request_day_report(
    session: ClientSession,
    url: str,
    access_token: str,
    appliance_id: int,
) -> dict[str, Any] | None:
    """Request the raw dayReportV2 result for an appliance.

    Returns
    -------
    dict[str, Any] | None
        The report result, or None when the cloud holds no report for the
        appliance.

    Raises
    ------
    MideaCloudAuthError
        If no access token is available or the token was rejected.
    MideaCloudReportError
        If the request failed or the cloud answered with an error.

    """
    if not access_token:
        msg = "No Midea cloud access token"
        raise MideaCloudAuthError(msg)
    headers = {
        "content-type": "application/json; charset=utf-8",
        "accessToken": access_token,
    }
    payload = {
        "msg": DAY_REPORT_MESSAGE,
        "params": {"applianceId": str(appliance_id)},
    }
    try:
        async with session.post(
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            data: dict[str, Any] = await response.json(content_type=None)
    except (ClientError, TimeoutError, ValueError) as err:
        raise MideaCloudReportError(str(err)) from err
    error_code = data.get("code")
    if error_code is not None:
        _raise_error(int(error_code), str(data.get("msg", "")))
    if str(data.get("retCode")) != "0":
        _raise_error(0, str(data.get("desc", data.get("retCode"))))
    result = data.get("result")
    return result if isinstance(result, dict) else None


class _ReportCloudMixin:
    """Mixin adding the E3 usage report request to a cloud implementation.

    The mixin only relies on the protected attributes every ``midealan.cloud``
    implementation already exposes to its subclasses, so no library change is
    needed to request the report.
    """

    _access_token: str | None
    _api_url: str
    _session: ClientSession

    async def async_get_day_report(self, appliance_id: int) -> dict[str, Any] | None:
        """Request the raw dayReportV2 result for an appliance.

        Returns
        -------
        dict[str, Any] | None
            The report result, or None when the cloud holds no report for the
            appliance.

        """
        return await request_day_report(
            self._session,
            f"{self._api_url}{REPORT_ALIAS}",
            self._access_token or "",
            appliance_id,
        )


class MeijuReportCloud(_ReportCloudMixin, MeijuCloud):
    """Meiju cloud with E3 usage report support."""


class SmartHomeReportCloud(_ReportCloudMixin, SmartHomeCloud):
    """MSmartHome cloud with E3 usage report support."""


ReportCloud = MeijuReportCloud | SmartHomeReportCloud


def create_report_cloud(
    cloud_name: str,
    session: ClientSession,
    account: str,
    password: str,
) -> ReportCloud:
    """Create a cloud client able to request the E3 usage report.

    Returns
    -------
    ReportCloud
        A cloud implementation extended with the usage report request.

    Raises
    ------
    MideaCloudReportError
        If the cloud is unknown or has no usage report support.

    """
    cloud_data = SUPPORTED_CLOUDS.get(cloud_name)
    if cloud_data is None:
        msg = f"Unsupported cloud: {cloud_name}"
        raise MideaCloudReportError(msg)
    class_name = cloud_data["class_name"]
    if class_name == "MeijuCloud":
        return MeijuReportCloud(
            cloud_name=cloud_name,
            session=session,
            account=account,
            password=password,
        )
    if class_name == "SmartHomeCloud":
        return SmartHomeReportCloud(
            cloud_name=cloud_name,
            session=session,
            account=account,
            password=password,
        )
    msg = f"Cloud {cloud_name} does not provide usage reports"
    raise MideaCloudReportError(msg)


@dataclass(frozen=True, slots=True)
class E3DayReport:
    """Parsed dayReportV2 data for an E3 gas water heater.

    ``*_daily`` is the most recent complete day, ``*_monthly`` the current
    month to date and ``*_last_month`` the previous calendar month. Water is in
    litres, gas in cubic metres and duration in minutes.
    """

    report_date: date
    water_daily: float | None
    gas_daily: float | None
    duration_daily: float | None
    water_monthly: float | None
    gas_monthly: float | None
    water_last_month: float | None
    gas_last_month: float | None
    water_daily_series: tuple[float, ...]
    gas_daily_series: tuple[float, ...]
    duration_daily_series: tuple[float, ...]


def _parse_series(value: Any, length: int) -> tuple[float, ...]:  # ruff:ignore[any-type]
    """Parse a comma separated numeric series, keeping the newest entries.

    Returns
    -------
    tuple[float, ...]
        The newest ``length`` values, or an empty tuple when absent/invalid.

    """
    if not isinstance(value, str):
        return ()
    parts = value.split(",")
    if len(parts) < length:
        return ()
    try:
        return tuple(float(part) for part in parts[-length:])
    except ValueError:
        return ()


def _latest(series: tuple[float, ...]) -> float | None:
    """Return the newest entry of a series.

    Returns
    -------
    float | None
        The last value, or None for an empty series.

    """
    return series[-1] if series else None


def _previous(series: tuple[float, ...]) -> float | None:
    """Return the entry before the newest one.

    Returns
    -------
    float | None
        The previous value, or None when the series is too short.

    """
    return series[-2] if len(series) > 1 else None


def _parse_report_date(value: Any) -> date:  # ruff:ignore[any-type]
    """Parse the report date, falling back to yesterday in local time.

    Returns
    -------
    date
        The date the report describes.

    """
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return cast("date", dt_util.now().date()) - timedelta(days=1)


def parse_day_report(result: dict[str, Any]) -> E3DayReport:
    """Parse a dayReportV2 ``result`` payload.

    Returns
    -------
    E3DayReport
        The parsed usage values.

    """
    water_daily = _parse_series(result.get("hotwaterUsem"), DAILY_SERIES_LENGTH)
    if not water_daily:
        water_daily = _parse_series(result.get("hotwaterUse7"), WEEK_SERIES_LENGTH)
    gas_daily = _parse_series(result.get("gasUsem"), DAILY_SERIES_LENGTH)
    if not gas_daily:
        gas_daily = _parse_series(result.get("gasUse7"), WEEK_SERIES_LENGTH)
    duration_daily = _parse_series(result.get("durTimem"), DAILY_SERIES_LENGTH)
    if not duration_daily:
        duration_daily = _parse_series(result.get("durTime7"), WEEK_SERIES_LENGTH)
    water_monthly = _parse_series(result.get("hotwaterUsey"), MONTHLY_SERIES_LENGTH)
    gas_monthly = _parse_series(result.get("gasUsey"), MONTHLY_SERIES_LENGTH)
    return E3DayReport(
        report_date=_parse_report_date(result.get("date")),
        water_daily=_latest(water_daily),
        gas_daily=_latest(gas_daily),
        duration_daily=_latest(duration_daily),
        water_monthly=_latest(water_monthly),
        gas_monthly=_latest(gas_monthly),
        water_last_month=_previous(water_monthly),
        gas_last_month=_previous(gas_monthly),
        water_daily_series=water_daily,
        gas_daily_series=gas_daily,
        duration_daily_series=duration_daily,
    )


class MideaCloudReportCoordinator(DataUpdateCoordinator[E3DayReport | None]):
    """Poll the Midea cloud usage report for one E3 appliance.

    The report is written once a day by the cloud, so an hourly poll only
    bounds how long a new day's values take to appear.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        credentials: CloudReportCredentials,
        appliance_id: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {appliance_id} usage report",
            update_interval=UPDATE_INTERVAL,
        )
        self._credentials = credentials
        self._appliance_id = appliance_id
        self._cloud: ReportCloud | None = None

    async def _async_update_data(self) -> E3DayReport | None:
        """Fetch and parse the usage report.

        Returns
        -------
        E3DayReport | None
            The parsed report, or None when the cloud has no report yet.

        Raises
        ------
        UpdateFailed
            If the cloud could not be reached or returned an error.

        """
        try:
            return await self._async_fetch()
        except MideaCloudAuthError:
            # The token expired or was rejected: drop the cached client and log
            # in again with the stored account when one is available.
            self._cloud = None
            try:
                return await self._async_fetch()
            except MideaCloudReportError as err:
                raise UpdateFailed(str(err)) from err
        except MideaCloudReportError as err:
            raise UpdateFailed(str(err)) from err

    async def _async_fetch(self) -> E3DayReport | None:
        """Fetch and parse the report, using the token or a fresh login.

        Returns
        -------
        E3DayReport | None
            The parsed report, or None when the cloud has no report yet.

        """
        if self._credentials.access_token:
            try:
                result = await self._async_request(self._credentials.access_token)
            except MideaCloudAuthError:
                if not self._credentials.has_login:
                    # A freshly stored token can need a moment to become valid
                    # server side; retry it once after a short delay.
                    await asyncio.sleep(AUTH_RETRY_DELAY)
                    result = await self._async_request(
                        self._credentials.access_token,
                    )
                    return None if result is None else parse_day_report(result)
                _LOGGER.debug(
                    "Stored Midea cloud token was rejected for device %s, "
                    "logging in again",
                    self._appliance_id,
                )
            else:
                return None if result is None else parse_day_report(result)
        cloud = await self._async_get_cloud()
        try:
            result = await cloud.async_get_day_report(self._appliance_id)
        except MideaCloudAuthError:
            # A token issued by a fresh login is rejected until the gateway
            # propagates it; retry the same token once after a short delay.
            await asyncio.sleep(AUTH_RETRY_DELAY)
            result = await cloud.async_get_day_report(self._appliance_id)
        return None if result is None else parse_day_report(result)

    async def _async_request(self, access_token: str) -> dict[str, Any] | None:
        """Request the report with an access token.

        Returns
        -------
        dict[str, Any] | None
            The raw report result, or None when the cloud has no report yet.

        """
        return await request_day_report(
            async_get_clientsession(self.hass),
            _report_url(self._credentials.cloud_name),
            access_token,
            self._appliance_id,
        )

    async def _async_get_cloud(self) -> ReportCloud:
        """Return a logged in report cloud, logging in on first use.

        Returns
        -------
        ReportCloud
            The cloud client holding a valid access token.

        Raises
        ------
        MideaCloudAuthError
            If no account is stored or the Midea cloud login failed.

        """
        if self._cloud is None:
            if not self._credentials.has_login:
                msg = "No Midea cloud account stored for a re-login"
                raise MideaCloudAuthError(msg)
            cloud = create_report_cloud(
                self._credentials.cloud_name,
                async_get_clientsession(self.hass),
                self._credentials.account,
                self._credentials.password,
            )
            if not await cloud.login():
                msg = "Midea cloud login failed"
                raise MideaCloudAuthError(msg)
            self._cloud = cloud
        return self._cloud
