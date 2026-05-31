"""Const for Midea Lan."""

from enum import IntEnum
from typing import Any, cast

from homeassistant.const import Platform

DOMAIN = "midea_ac_lan"
COMPONENT = "component"
DEVICES = "devices"

CONF_KEY = "key"
CONF_MODEL = "model"
CONF_SUBTYPE = "subtype"
CONF_ACCOUNT = "account"
CONF_SERVER = "server"
CONF_REFRESH_INTERVAL = "refresh_interval"

EXTRA_SENSOR = [Platform.SENSOR, Platform.BINARY_SENSOR]
EXTRA_SWITCH = [Platform.SWITCH, Platform.LOCK, Platform.SELECT, Platform.NUMBER]
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


class FanSpeed(IntEnum):
    """FanSpeed reference values."""

    LOW = 20
    MEDIUM = 40
    HIGH = 60
    FULL_SPEED = 80
    AUTO = 100
