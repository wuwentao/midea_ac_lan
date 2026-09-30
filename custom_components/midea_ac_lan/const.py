"""Const for Midea Lan."""

from enum import IntEnum
from typing import Any, cast

from homeassistant.const import Platform
from midealan.cloud import SUPPORTED_CLOUDS

DOMAIN = "midea_ac_lan"
COMPONENT = "component"
DEVICES = "devices"

CONF_KEY = "key"
CONF_MODEL = "model"
CONF_SUBTYPE = "subtype"
CONF_ACCOUNT = "account"
CONF_SERVER = "server"
CONF_SN = "sn"
CONF_REFRESH_INTERVAL = "refresh_interval"
CONF_MAC = "mac"

# Select DEFAULT_CLOUD from the list of supported cloud
DEFAULT_CLOUD: str = list(SUPPORTED_CLOUDS)[3]

# Only these clouds expose the E3 dayReportV2 usage report (their API URL uses
# the per-cloud proxy alias); the others raise CloudError before sending the
# request. Keep DEFAULT_CLOUD for the preset-login flow and use these for the
# E3 usage statistics options and coordinator fallback.
REPORT_CLOUDS: tuple[str, ...] = ("美的美居", "SmartHome")
DEFAULT_REPORT_CLOUD: str = REPORT_CLOUDS[0]

EXTRA_SENSOR = [Platform.SENSOR, Platform.BINARY_SENSOR]
EXTRA_SWITCH = [
    Platform.SWITCH,
    Platform.LOCK,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.TIME,
]
EXTRA_CONTROL = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.WATER_HEATER,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.LIGHT,
    *EXTRA_SWITCH,
]
ALL_PLATFORM = EXTRA_SENSOR + EXTRA_CONTROL


def supports_model(model: object, config: dict[str, Any]) -> bool:
    """Return if the entity config applies to the device model.

    Returns
    -------
    True if the entity is available for the device model.

    """
    models = config.get("models")
    return not models or str(model) in cast("list[str]", models)


def supports_device(
    model: object,
    subtype: object,
    config: dict[str, Any],
) -> bool:
    """Return if the entity config applies to the device model and subtype.

    Returns
    -------
    True if the entity supports the device model and subtype.

    """
    if config.get("removed"):
        return False
    normalized_subtype = int(cast("int", subtype))
    excluded_devices = cast(
        "list[tuple[str, int]]",
        config.get("excluded_devices", []),
    )
    if (str(model), normalized_subtype) in excluded_devices:
        return False
    excluded_subtypes = config.get("excluded_subtypes")
    if excluded_subtypes and normalized_subtype in cast(
        "list[int]",
        excluded_subtypes,
    ):
        return False
    subtypes = config.get("subtypes")
    return supports_model(model, config) and (
        not subtypes or normalized_subtype in cast("list[int]", subtypes)
    )


class FanSpeed(IntEnum):
    """FanSpeed reference values."""

    LOW = 20
    MEDIUM = 40
    HIGH = 60
    FULL_SPEED = 80
    AUTO = 100
