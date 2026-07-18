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

if TYPE_CHECKING:
    from datetime import date, datetime

    from midealocal.device import MideaDevice

COMPRESSOR_FREQUENCY: Final = "compressor_frequency"
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
SUPPORTED_AC_BB_DIAGNOSTIC_MODELS: Final = frozenset({("23096725", 1)})

_BB_BODY_TYPE: Final = 0xBB
_AC_DEVICE_TYPE: Final = 0xAC
_OUTDOOR_DIAGNOSTICS_TYPE: Final = 0x30
_MESSAGE_BODY_OFFSET: Final = 10
_SUBPROTOCOL_BODY_OFFSET: Final = 16
_CURRENT_OFFSET: Final = 10
_FREQUENCY_OFFSET: Final = 11
_POWER_FACTOR_OFFSET: Final = 32
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
    return (str(model), int(subtype)) in SUPPORTED_AC_BB_DIAGNOSTIC_MODELS


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
        if (
            len(message) <= _SUBPROTOCOL_BODY_OFFSET + _POWER_FACTOR_OFFSET
            or message[_MESSAGE_BODY_OFFSET] != _BB_BODY_TYPE
            or message[_SUBPROTOCOL_BODY_OFFSET - 1] != _OUTDOOR_DIAGNOSTICS_TYPE
        ):
            return None

        body = message[_SUBPROTOCOL_BODY_OFFSET:]
        powered = bool(device.get_attribute(ACAttributes.power))
        now = monotonic()
        today = _local_date()
        if self.energy_date != today:
            self.daily_energy = 0.0
            self.energy_date = today
            self.daily_restored = True

        if powered:
            compressor_current = body[_CURRENT_OFFSET] * self.current_scale
            compressor_frequency = float(body[_FREQUENCY_OFFSET])
            reported_power_factor = body[_POWER_FACTOR_OFFSET] / 100
            power_factor = (
                reported_power_factor
                if 0 < reported_power_factor <= 1
                else self.default_power_factor
            )
            estimated_power = compressor_current * self.voltage * power_factor
        else:
            compressor_current = 0.0
            compressor_frequency = 0.0
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
    )
    state.default_power_factor = min(state.default_power_factor, 1.0)
    vars(device)[_STATE_KEY] = state
    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    attributes.update(dict.fromkeys(BB_DIAGNOSTIC_ATTRIBUTES))
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
