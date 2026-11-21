"""Permanent CA mode support for verified Midea refrigerators.

This module keeps the CA write path deliberately narrow: it captures the last
real status body, changes only codeMode byte 1, and lets midea-lan build the
LAN frame and V3 transport.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

CA_MODE_BODY_LENGTH = 61
CA_MODE_BODY_MAX_AGE_SECONDS = 120.0
CA_MODE_MODEL = "310Z999Z"
CA_MODE_SUBTYPE = 56
CA_MODE_MASKS = {
    "storage_mode": 0x01,
    "freezing_mode": 0x02,
    "holiday_mode": 0x10,
}
CA_MODE_ENTITY_ATTRIBUTES = frozenset(CA_MODE_MASKS)

_capture_lock = threading.RLock()
_capture_installed = False
_latest_body: "_CABody | None" = None


@dataclass(frozen=True)
class _CABody:
    body: bytes
    monotonic: float
    received_at: datetime
    generation: int


def supports_ca_modes(device: object) -> bool:
    """Return whether the verified CA mode implementation applies."""
    return (
        getattr(device, "device_type", None) == 0xCA
        and str(getattr(device, "model", "")) == CA_MODE_MODEL
        and int(getattr(device, "subtype", -1)) == CA_MODE_SUBTYPE
    )


def _capture_status_body(body: bytes) -> None:
    """Capture a copy of the parser body after it has been accepted."""
    global _latest_body  # noqa: PLW0603
    if len(body) < CA_MODE_BODY_LENGTH:
        return
    now = time.monotonic()
    with _capture_lock:
        generation = 1 if _latest_body is None else _latest_body.generation + 1
        _latest_body = _CABody(
            body=bytes(body[:CA_MODE_BODY_LENGTH]),
            monotonic=now,
            received_at=datetime.now().astimezone(),
            generation=generation,
        )


def install_ca_parser_capture() -> None:
    """Install the in-process observational hook once."""
    global _capture_installed  # noqa: PLW0603
    with _capture_lock:
        if _capture_installed:
            return

        from midealan.devices.ca.message import MessageCAResponse

        original_init = MessageCAResponse.__init__

        def _init(self: MessageCAResponse, message: bytes) -> None:
            original_init(self, message)
            try:
                body = bytes(self.body)
            except (AttributeError, TypeError):
                return
            _capture_status_body(body)

        MessageCAResponse.__init__ = _init  # type: ignore[method-assign]
        _capture_installed = True


def _fresh_body() -> _CABody | None:
    with _capture_lock:
        current = _latest_body
        if current is None:
            return None
        if time.monotonic() - current.monotonic > CA_MODE_BODY_MAX_AGE_SECONDS:
            return None
        return current


def build_mode_body(body: bytes | bytearray, mask: int, enabled: bool) -> bytes:
    """Return a 61-byte read-modify-write body changing only codeMode."""
    if len(body) < CA_MODE_BODY_LENGTH:
        raise ValueError("CA status body is shorter than 61 bytes")
    result = bytearray(body[:CA_MODE_BODY_LENGTH])
    result[1] = (result[1] | mask) if enabled else (result[1] & ~mask)
    return bytes(result)


def _mode_values(body: bytes) -> dict[str, bool]:
    code_mode = body[1]
    return {
        "storage_mode": bool(code_mode & 0x01),
        "freezing_mode": bool(code_mode & 0x02),
        "holiday_mode": bool(code_mode & 0x10),
    }


def attach_ca_mode_support(device: object) -> None:
    """Attach cache-aware read/write behavior to one verified CA device."""
    if not supports_ca_modes(device):
        return

    install_ca_parser_capture()
    if getattr(device, "_ca_modes_attached", False):
        return

    original_process_message = device.process_message
    original_set_attribute = device.set_attribute
    device._ca_modes_attached = True
    device._ca_modes_lock = threading.RLock()
    device._ca_modes_generation = 0
    device._ca_modes_pending_generation = None

    def _process_message(message: bytes) -> dict[str, object]:
        new_status = original_process_message(message)
        current = _fresh_body()
        if current is None:
            code_mode = device._attributes.get("code_mode")
            if code_mode is not None:
                new_status["storage_mode"] = bool(code_mode)
                device._attributes["storage_mode"] = bool(code_mode)
            return new_status
        if current.generation == device._ca_modes_generation:
            return new_status

        values = _mode_values(current.body)
        device._ca_modes_generation = current.generation
        if (
            device._ca_modes_pending_generation is not None
            and current.generation > device._ca_modes_pending_generation
        ):
            device._ca_modes_pending_generation = None

        for attribute, value in values.items():
            device._attributes[attribute] = value
            new_status[attribute] = value
        return new_status

    def _set_attribute(attr: str, value: bool | float | str) -> None:
        mask = CA_MODE_MASKS.get(attr)
        if mask is None:
            original_set_attribute(attr, value)
            return

        enabled = value is True or value == 1 or value == "true"
        with device._ca_modes_lock:
            current = _fresh_body()
            if current is None:
                _LOGGER.warning(
                    "CA mode write refused: no fresh status body available",
                )
                return
            if (
                device._ca_modes_pending_generation is not None
                and current.generation <= device._ca_modes_pending_generation
            ):
                _LOGGER.warning(
                    "CA mode write refused: waiting for status after previous SET",
                )
                return

            body = build_mode_body(current.body, mask, enabled)
            if body[1] == current.body[1]:
                return

            # Device.send_command() is the existing midea-lan path:
            # body -> MessageQuestCustom -> serialize -> PacketBuilder/V3.
            device._ca_modes_pending_generation = current.generation
            try:
                device.send_command(2, body)
            except Exception:
                _LOGGER.exception("CA mode SET failed during transport")
                raise

    device.process_message = _process_message
    device.set_attribute = _set_attribute


__all__ = [
    "CA_MODE_ENTITY_ATTRIBUTES",
    "attach_ca_mode_support",
    "build_mode_body",
    "supports_ca_modes",
]

