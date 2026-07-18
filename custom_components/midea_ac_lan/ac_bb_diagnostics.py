"""Diagnostics exposed by the newer AC BB subprotocol.

Some newer Midea air conditioners use the BB subprotocol and do not implement
the traditional 0x44 energy query.  Their 0x30 outdoor-unit diagnostics still
contain compressor current, frequency, and power factor.  This compatibility
layer extracts those fields without changing the external ``midea-local``
package.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from time import monotonic
from typing import TYPE_CHECKING, Any, Final, cast

from homeassistant.util import dt as dt_util
from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.ac.message import MessageSubProtocolSet

if TYPE_CHECKING:
    from datetime import date, datetime

    from midealocal.device import MideaDevice

COMPRESSOR_FREQUENCY: Final = "compressor_frequency"
COMPRESSOR_TARGET_FREQUENCY: Final = "compressor_target_frequency"
COMPRESSOR_CURRENT: Final = "compressor_current"
ESTIMATED_REALTIME_POWER: Final = "estimated_realtime_power"
ESTIMATED_TOTAL_ENERGY_CONSUMPTION: Final = "estimated_total_energy_consumption"
ESTIMATED_DAILY_ENERGY_CONSUMPTION: Final = "estimated_daily_energy_consumption"

BB_DIAGNOSTIC_ATTRIBUTES: Final = (
    COMPRESSOR_FREQUENCY,
    COMPRESSOR_CURRENT,
    ESTIMATED_REALTIME_POWER,
    ESTIMATED_TOTAL_ENERGY_CONSUMPTION,
    ESTIMATED_DAILY_ENERGY_CONSUMPTION,
)
BB_ENERGY_ATTRIBUTES: Final = frozenset(
    {
        ESTIMATED_TOTAL_ENERGY_CONSUMPTION,
        ESTIMATED_DAILY_ENERGY_CONSUMPTION,
    },
)

# Model identifiers are reported by the Midea cloud and are shared by every
# appliance of the same product model.  Do not use appliance/device IDs here.
SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES: Final = {
    ("23096725", 1): frozenset(BB_DIAGNOSTIC_ATTRIBUTES),
    ("23096633", 1): frozenset(
        {
            COMPRESSOR_FREQUENCY,
            COMPRESSOR_TARGET_FREQUENCY,
        },
    ),
}
SUPPORTED_AC_BB_PROTOCOL_MODELS: Final = frozenset({("23096633", 1)})

_BB_BODY_TYPE: Final = 0xBB
_AC_DEVICE_TYPE: Final = 0xAC
_OUTDOOR_DIAGNOSTICS_TYPE: Final = 0x30
_BASIC_STATUS_TYPE: Final = 0x11
_MESSAGE_BODY_OFFSET: Final = 10
_SUBPROTOCOL_BODY_OFFSET: Final = 16
_TARGET_FREQUENCY_OFFSET: Final = 10
_ACTUAL_FREQUENCY_OFFSET: Final = 11
_CURRENT_OFFSET: Final = 10
_POWER_FACTOR_OFFSET: Final = 32
_FRESH_AIR_SWITCH_OFFSET: Final = 45
_FRESH_AIR_SPEED_OFFSET: Final = 46
_MAX_INTEGRATION_INTERVAL_SECONDS: Final = 120.0

_DEFAULT_VOLTAGE: Final = 220.0
_DEFAULT_CURRENT_SCALE: Final = 0.1
_DEFAULT_POWER_FACTOR: Final = 0.95
_STATE_KEY: Final = "_midea_ac_lan_bb_diagnostics_state"

_LOGGER = logging.getLogger(__name__)


def _local_date() -> date:
    """Return the current Home Assistant local date.

    Returns
    -------
    Current date in Home Assistant's configured time zone.

    """
    return dt_util.now().date()


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


def _fresh_air_mode(power: bool, speed: int) -> str:
    """Return the nearest Midea fresh-air preset for a reported speed.

    Returns
    -------
    Preset name matching the reported power and speed.

    """
    if not power:
        return "off"
    mode = "off"
    for threshold, name in (
        (20, "silent"),
        (40, "low"),
        (60, "medium"),
        (80, "high"),
        (100, "full"),
    ):
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
            len(message) > _SUBPROTOCOL_BODY_OFFSET + _FRESH_AIR_SPEED_OFFSET
            and message[_MESSAGE_BODY_OFFSET] == _BB_BODY_TYPE
            and message[_SUBPROTOCOL_BODY_OFFSET - 1] == _BASIC_STATUS_TYPE
        ):
            body = message[_SUBPROTOCOL_BODY_OFFSET:]
            fresh_air_power = bool(body[_FRESH_AIR_SWITCH_OFFSET] & 0x01)
            fresh_air_speed = int(body[_FRESH_AIR_SPEED_OFFSET])
            fresh_air_mode = _fresh_air_mode(fresh_air_power, fresh_air_speed)
            fresh_air_status = {
                ACAttributes.fresh_air_power: fresh_air_power,
                ACAttributes.fresh_air_fan_speed: fresh_air_speed,
                ACAttributes.fresh_air_mode: fresh_air_mode,
            }
            attributes.update(fresh_air_status)
            status.update({str(key): value for key, value in fresh_air_status.items()})
            _LOGGER.debug(
                "[%s] BB fresh-air status: power=%s, speed=%s, mode=%s",
                device.device_id,
                fresh_air_power,
                fresh_air_speed,
                fresh_air_mode,
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

    def __init__(self, protocol_version: int, power: bool, speed: int) -> None:
        """Initialize a model-specific fresh-air control command."""
        super().__init__(protocol_version)
        self._subprotocol_query_type = 0xC0
        self._fresh_air_power = power
        self._fresh_air_speed = max(1, min(speed, 100))

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
        body[cursor + 6] = 0x04
        body[cursor + 7] = 0x04 if self._fresh_air_power else 0x00
        body[cursor + 55] = 0x80 | self._fresh_air_speed
        body[95] = (-sum(body[12:95])) & 0xFF
        return body


def set_ac_bb_fresh_air(
    device: MideaDevice,
    power: bool,
    speed: int,
) -> None:
    """Send the verified model-specific fresh-air single-control command."""
    protocol_version = cast("int", vars(device)["_message_protocol_version"])
    device.build_send(
        _MessageBBFreshAirSet(
            protocol_version,
            power,
            speed,
        ),
    )


@dataclass
class _BBDiagnosticsState:
    """Runtime state for one BB air conditioner."""

    voltage: float = _DEFAULT_VOLTAGE
    current_scale: float = _DEFAULT_CURRENT_SCALE
    default_power_factor: float = _DEFAULT_POWER_FACTOR
    last_update: float | None = None
    last_power: float = 0.0
    total_energy: float = 0.0
    daily_energy: float = 0.0
    energy_date: date = field(default_factory=_local_date)
    was_powered: bool = False
    total_restored: bool = False
    daily_restored: bool = False
    frequency_only: bool = False

    def process(
        self,
        device: MideaDevice,
        message: bytes,
    ) -> dict[str, float | int] | None:
        """Extract the supported fields from an outdoor diagnostics frame.

        Returns
        -------
        Parsed diagnostics, or ``None`` when the frame is not BB type 0x30.

        """
        required_offset = (
            _ACTUAL_FREQUENCY_OFFSET if self.frequency_only else _POWER_FACTOR_OFFSET
        )
        if (
            len(message) <= _SUBPROTOCOL_BODY_OFFSET + required_offset
            or message[_MESSAGE_BODY_OFFSET] != _BB_BODY_TYPE
            or message[_SUBPROTOCOL_BODY_OFFSET - 1] != _OUTDOOR_DIAGNOSTICS_TYPE
        ):
            return None

        body = message[_SUBPROTOCOL_BODY_OFFSET:]
        powered = bool(device.get_attribute(ACAttributes.power))
        target_frequency = float(body[_TARGET_FREQUENCY_OFFSET]) if powered else 0.0
        compressor_frequency = float(body[_ACTUAL_FREQUENCY_OFFSET]) if powered else 0.0
        if self.frequency_only:
            return {
                COMPRESSOR_FREQUENCY: round(compressor_frequency),
                COMPRESSOR_TARGET_FREQUENCY: round(target_frequency),
            }

        now = monotonic()
        today = _local_date()
        if self.energy_date != today:
            self.daily_energy = 0.0
            self.energy_date = today
            self.daily_restored = True

        if powered:
            compressor_current = body[_CURRENT_OFFSET] * self.current_scale
            reported_power_factor = body[_POWER_FACTOR_OFFSET] / 100
            power_factor = (
                reported_power_factor
                if 0 < reported_power_factor <= 1
                else self.default_power_factor
            )
            estimated_power = compressor_current * self.voltage * power_factor
        else:
            compressor_current = 0.0
            estimated_power = 0.0

        if self.last_update is not None and self.was_powered:
            elapsed = now - self.last_update
            if elapsed <= _MAX_INTEGRATION_INTERVAL_SECONDS:
                average_power = (self.last_power + estimated_power) / 2
                energy_delta = average_power * elapsed / 3_600_000
                self.total_energy += energy_delta
                self.daily_energy += energy_delta

        self.last_update = now
        self.last_power = estimated_power
        self.was_powered = powered

        return {
            COMPRESSOR_FREQUENCY: round(compressor_frequency),
            COMPRESSOR_CURRENT: round(compressor_current, 1),
            ESTIMATED_REALTIME_POWER: round(estimated_power),
            ESTIMATED_TOTAL_ENERGY_CONSUMPTION: round(self.total_energy, 4),
            ESTIMATED_DAILY_ENERGY_CONSUMPTION: round(self.daily_energy, 4),
        }


def restore_ac_bb_energy(
    device: MideaDevice,
    attribute: str,
    value: float,
    last_updated: datetime,
) -> None:
    """Restore a cumulative BB energy value into its runtime state."""
    state = vars(device).get(_STATE_KEY)
    if not isinstance(state, _BBDiagnosticsState):
        return

    restored_value = max(value, 0.0)
    if attribute == ESTIMATED_TOTAL_ENERGY_CONSUMPTION:
        if not state.total_restored:
            state.total_energy += restored_value
            state.total_restored = True
        current_value = state.total_energy
    elif attribute == ESTIMATED_DAILY_ENERGY_CONSUMPTION:
        if not state.daily_restored:
            if dt_util.as_local(last_updated).date() == state.energy_date:
                state.daily_energy += restored_value
            state.daily_restored = True
        current_value = state.daily_energy
    else:
        return

    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    attributes[attribute] = round(current_value, 4)


def _customize_number(
    customize: dict[str, Any],
    key: str,
    default: float,
) -> float:
    """Return a positive numeric customization or its default.

    Returns
    -------
    The customized number when valid, otherwise ``default``.

    """
    value = customize.get(key, default)
    if isinstance(value, (int, float)) and value > 0:
        return float(value)
    return default


def install_ac_bb_diagnostics(device: MideaDevice, customize_json: str) -> None:
    """Install the BB diagnostics parser on an AC device instance."""
    if not supports_ac_bb_diagnostics(
        device.device_type,
        device.model,
        device.subtype,
    ):
        return

    customize: dict[str, Any] = {}
    if customize_json:
        try:
            parsed = json.loads(customize_json)
            if isinstance(parsed, dict):
                customize = parsed
        except (TypeError, ValueError):
            _LOGGER.debug(
                "[%s] Unable to parse customize JSON for BB diagnostics",
                device.device_id,
            )

    state = _BBDiagnosticsState(
        voltage=_customize_number(
            customize,
            "bb_power_voltage",
            _DEFAULT_VOLTAGE,
        ),
        current_scale=_customize_number(
            customize,
            "bb_current_scale",
            _DEFAULT_CURRENT_SCALE,
        ),
        default_power_factor=_customize_number(
            customize,
            "bb_power_factor",
            _DEFAULT_POWER_FACTOR,
        ),
        frequency_only=(str(device.model), int(device.subtype)) == ("23096633", 1),
    )
    state.default_power_factor = min(state.default_power_factor, 1.0)
    vars(device)[_STATE_KEY] = state
    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    diagnostic_attributes = SUPPORTED_AC_BB_DIAGNOSTIC_ATTRIBUTES[
        str(device.model),
        int(device.subtype),
    ]
    attributes.update(dict.fromkeys(diagnostic_attributes))
    original_process_message = device.process_message

    def process_message(message: bytes) -> dict[str, Any]:
        status = original_process_message(message)
        diagnostics = state.process(device, message)
        if diagnostics is not None:
            attributes.update(diagnostics)
            status.update(diagnostics)
            _LOGGER.debug(
                "[%s] BB compressor diagnostics: %s",
                device.device_id,
                diagnostics,
            )
        return status

    device.process_message = process_message  # type: ignore[method-assign]
