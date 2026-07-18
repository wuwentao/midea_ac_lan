"""Model-gated compatibility for verified fields in the AC BB subprotocol."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final, cast

from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.ac.message import MessageSubProtocolSet

if TYPE_CHECKING:
    from midealocal.device import MideaDevice

COMPRESSOR_FREQUENCY: Final = "compressor_frequency"
COMPRESSOR_TARGET_FREQUENCY: Final = "compressor_target_frequency"
FRESH_AIR_EXHAUST: Final = "fresh_air_exhaust"
FRESH_AIR_EXHAUST_POWER: Final = "fresh_air_exhaust_power"
FRESH_AIR_EXHAUST_SPEED: Final = "fresh_air_exhaust_speed"
FRESH_AIR_EXHAUST_MODE: Final = "fresh_air_exhaust_mode"

# Model identifiers are reported by the Midea cloud and are shared by every
# appliance of the same product model.  Do not use appliance/device IDs here.
SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES: Final = {
    ("23096725", 1): frozenset({COMPRESSOR_FREQUENCY}),
    ("23096633", 1): frozenset(
        {
            COMPRESSOR_FREQUENCY,
            COMPRESSOR_TARGET_FREQUENCY,
        },
    ),
}
SUPPORTED_AC_BB_PROTOCOL_MODELS: Final = frozenset({("23096633", 1)})
SUPPORTED_AC_BB_EXHAUST_MODELS: Final = frozenset({("23096633", 1)})

_BB_BODY_TYPE: Final = 0xBB
_AC_DEVICE_TYPE: Final = 0xAC
_OUTDOOR_DIAGNOSTICS_TYPE: Final = 0x30
_BASIC_STATUS_TYPE: Final = 0x11
_MESSAGE_BODY_OFFSET: Final = 10
_SUBPROTOCOL_BODY_OFFSET: Final = 16
_TARGET_FREQUENCY_OFFSET: Final = 10
_ACTUAL_FREQUENCY_OFFSET: Final = 11
_FRESH_AIR_SWITCH_OFFSET: Final = 45
_FRESH_AIR_INTAKE_SPEED_OFFSET: Final = 46
_FRESH_AIR_EXHAUST_SPEED_OFFSET: Final = 47

BB_FRESH_AIR_INTAKE_PRESETS: Final = {
    0: "off",
    40: "low",
    60: "medium",
    80: "high",
    100: "full",
}
BB_FRESH_AIR_EXHAUST_PRESETS: Final = {
    0: "off",
    20: "silent",
    80: "high",
    100: "full",
}

_LOGGER = logging.getLogger(__name__)


def supports_ac_bb_diagnostics(
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether an appliance belongs to a supported BB AC model.

    Returns
    -------
    ``True`` only for a known 0xAC model/subtype combination.

    """
    if device_type != _AC_DEVICE_TYPE or subtype is None:
        return False
    return (str(model), int(subtype)) in SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES


def supports_ac_bb_diagnostic_attribute(
    attribute: str,
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether a BB diagnostic attribute is verified for a model.

    Returns
    -------
    ``True`` only when the exact model/subtype reports the attribute.

    """
    if device_type != _AC_DEVICE_TYPE or subtype is None:
        return False
    attributes = SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES.get(
        (str(model), int(subtype)),
        frozenset(),
    )
    return attribute in attributes


def supports_ac_bb_protocol(
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether an appliance must start directly with the BB protocol.

    Returns
    -------
    ``True`` only for a verified 0xAC model/subtype combination.

    """
    if device_type != _AC_DEVICE_TYPE or subtype is None:
        return False
    return (str(model), int(subtype)) in SUPPORTED_AC_BB_PROTOCOL_MODELS


def supports_ac_bb_exhaust(
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether an appliance exposes controllable BB exhaust airflow.

    Returns
    -------
    ``True`` only for a verified 0xAC model/subtype combination.

    """
    if device_type != _AC_DEVICE_TYPE or subtype is None:
        return False
    return (str(model), int(subtype)) in SUPPORTED_AC_BB_EXHAUST_MODELS


def _fresh_air_mode(power: bool, speed: int, *, exhaust: bool = False) -> str:
    """Return the nearest Midea fresh-air preset for a reported speed.

    Returns
    -------
    Preset name matching the reported power and speed.

    """
    if not power:
        return "off"
    presets = BB_FRESH_AIR_EXHAUST_PRESETS if exhaust else BB_FRESH_AIR_INTAKE_PRESETS
    mode = "off"
    for threshold, name in presets.items():
        if speed < threshold:
            break
        mode = name
    return mode


def install_ac_bb_protocol(device: MideaDevice) -> None:
    """Select BB queries and install verified model-specific status parsing."""
    if not supports_ac_bb_protocol(
        device.device_type,
        device.model,
        device.subtype,
    ):
        return

    vars(device)["_used_subprotocol"] = True
    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    original_process_message = device.process_message

    def process_message(message: bytes) -> dict[str, Any]:
        status = original_process_message(message)
        if (
            len(message) > _SUBPROTOCOL_BODY_OFFSET + _FRESH_AIR_EXHAUST_SPEED_OFFSET
            and message[_MESSAGE_BODY_OFFSET] == _BB_BODY_TYPE
            and message[_SUBPROTOCOL_BODY_OFFSET - 1] == _BASIC_STATUS_TYPE
        ):
            body = message[_SUBPROTOCOL_BODY_OFFSET:]
            fresh_air_power = bool(body[_FRESH_AIR_SWITCH_OFFSET] & 0x01)
            fresh_air_speed = int(body[_FRESH_AIR_INTAKE_SPEED_OFFSET])
            fresh_air_mode = _fresh_air_mode(fresh_air_power, fresh_air_speed)
            exhaust_power = bool(body[_FRESH_AIR_SWITCH_OFFSET] & 0x02)
            exhaust_speed = int(body[_FRESH_AIR_EXHAUST_SPEED_OFFSET])
            exhaust_mode = _fresh_air_mode(
                exhaust_power,
                exhaust_speed,
                exhaust=True,
            )
            fresh_air_status = {
                ACAttributes.fresh_air_power: fresh_air_power,
                ACAttributes.fresh_air_fan_speed: fresh_air_speed,
                ACAttributes.fresh_air_mode: fresh_air_mode,
                FRESH_AIR_EXHAUST_POWER: exhaust_power,
                FRESH_AIR_EXHAUST_SPEED: exhaust_speed,
                FRESH_AIR_EXHAUST_MODE: exhaust_mode,
            }
            attributes.update(fresh_air_status)
            status.update({str(key): value for key, value in fresh_air_status.items()})
            _LOGGER.debug(
                "[%s] BB fresh-air status: intake=%s/%s/%s, exhaust=%s/%s/%s",
                device.device_id,
                fresh_air_power,
                fresh_air_speed,
                fresh_air_mode,
                exhaust_power,
                exhaust_speed,
                exhaust_mode,
            )
        return status

    device.process_message = process_message  # type: ignore[method-assign]
    _LOGGER.debug(
        "[%s] Starting model %s subtype %s with the BB subprotocol",
        device.device_id,
        device.model,
        device.subtype,
    )


class _MessageBBFreshAirSet(MessageSubProtocolSet):
    """Model 23096633 C0/02 single-control fresh-air command."""

    def __init__(
        self,
        protocol_version: int,
        power: bool,
        speed: int,
        exhaust: bool,
    ) -> None:
        """Initialize a model-specific fresh-air control command."""
        super().__init__(protocol_version)
        self._subprotocol_query_type = 0xC0
        self._fresh_air_power = power
        self._fresh_air_speed = max(1, min(speed, 100))
        self._exhaust = exhaust

    @property
    def _subprotocol_body(self) -> bytearray:
        body = bytearray(96)
        body[1] = 0x01
        body[2] = 0x01
        body[11] = 0x01
        body[12] = 0xC0
        body[13] = 0x02
        body[14] = 0x54
        cursor = 15
        switch_mask = 0x08 if self._exhaust else 0x04
        speed_offset = 56 if self._exhaust else 55
        body[cursor + 6] = switch_mask
        body[cursor + 7] = switch_mask if self._fresh_air_power else 0x00
        body[cursor + speed_offset] = 0x80 | self._fresh_air_speed
        body[95] = (-sum(body[12:95])) & 0xFF
        return body


def set_ac_bb_fresh_air(
    device: MideaDevice,
    power: bool,
    speed: int,
    *,
    exhaust: bool = False,
) -> None:
    """Send the verified model-specific fresh-air single-control command."""
    speed = max(1, min(speed, 100))
    protocol_version = cast("int", vars(device)["_message_protocol_version"])
    device.build_send(
        _MessageBBFreshAirSet(
            protocol_version,
            power,
            speed,
            exhaust,
        ),
    )
    mode = _fresh_air_mode(power, speed, exhaust=exhaust)
    fresh_air_status = (
        {
            FRESH_AIR_EXHAUST_POWER: power,
            FRESH_AIR_EXHAUST_SPEED: speed,
            FRESH_AIR_EXHAUST_MODE: mode,
        }
        if exhaust
        else {
            ACAttributes.fresh_air_power: power,
            ACAttributes.fresh_air_fan_speed: speed,
            ACAttributes.fresh_air_mode: mode,
        }
    )
    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    attributes.update(fresh_air_status)
    device.update_all({str(key): value for key, value in fresh_air_status.items()})


def install_ac_bb_diagnostics(device: MideaDevice) -> None:
    """Install the BB diagnostics parser on an AC device instance."""
    if not supports_ac_bb_diagnostics(
        device.device_type,
        device.model,
        device.subtype,
    ):
        return

    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    diagnostic_attributes = SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES[
        str(device.model),
        int(device.subtype),
    ]
    attributes.update(dict.fromkeys(diagnostic_attributes))
    original_process_message = device.process_message

    def process_message(message: bytes) -> dict[str, Any]:
        status = original_process_message(message)
        if (
            len(message) <= _SUBPROTOCOL_BODY_OFFSET + _ACTUAL_FREQUENCY_OFFSET
            or message[_MESSAGE_BODY_OFFSET] != _BB_BODY_TYPE
            or message[_SUBPROTOCOL_BODY_OFFSET - 1] != _OUTDOOR_DIAGNOSTICS_TYPE
        ):
            return status

        body = message[_SUBPROTOCOL_BODY_OFFSET:]
        diagnostics = {
            COMPRESSOR_FREQUENCY: int(body[_ACTUAL_FREQUENCY_OFFSET]),
        }
        if COMPRESSOR_TARGET_FREQUENCY in diagnostic_attributes:
            diagnostics[COMPRESSOR_TARGET_FREQUENCY] = int(
                body[_TARGET_FREQUENCY_OFFSET],
            )
        attributes.update(diagnostics)
        status.update(diagnostics)
        _LOGGER.debug(
            "[%s] BB compressor diagnostics: %s",
            device.device_id,
            diagnostics,
        )
        return status

    device.process_message = process_message  # type: ignore[method-assign]
