"""Model-specific diagnostics from the traditional AC C1 protocol.

Some multi-split indoor units expose outdoor-unit operating data through C1
group 0x41, but ``midea-local`` does not currently query or parse that group.
This compatibility layer adds the read-only query only for models verified to
support it and exposes their reported compressor frequencies.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final, cast

from midealocal.crc8 import calculate
from midealocal.devices.ac.message import MessageACBase
from midealocal.message import ListTypes, MessageType

from .ac_bb_diagnostics import (
    COMPRESSOR_FREQUENCY,
    COMPRESSOR_TARGET_FREQUENCY,
    supports_ac_bb_diagnostic_attribute,
)

if TYPE_CHECKING:
    from midealocal.device import MideaDevice

SUPPORTED_AC_C1_FREQUENCY_MODELS: Final = frozenset(
    {
        ("22390001", 8),
        ("22390003", 8),
    },
)

AC_C1_DIAGNOSTIC_ATTRIBUTES: Final = frozenset(
    {
        COMPRESSOR_FREQUENCY,
        COMPRESSOR_TARGET_FREQUENCY,
    },
)

_AC_DEVICE_TYPE: Final = 0xAC
_C1_BODY_TYPE: Final = 0xC1
_GROUP_ONE_TYPE: Final = 0x41
_MESSAGE_BODY_OFFSET: Final = 10
_GROUP_TYPE_OFFSET: Final = _MESSAGE_BODY_OFFSET + 3
_ACTUAL_FREQUENCY_OFFSET: Final = _MESSAGE_BODY_OFFSET + 4
_TARGET_FREQUENCY_OFFSET: Final = _MESSAGE_BODY_OFFSET + 5

_LOGGER = logging.getLogger(__name__)


class _MessageGroupOneQuery(MessageACBase):
    """Read-only AC C1 group 0x41 query."""

    def __init__(self, protocol_version: int) -> None:
        """Initialize the group query."""
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=ListTypes.X41,
        )

    @property
    def _body(self) -> bytearray:
        return bytearray([0x21, 0x01, _GROUP_ONE_TYPE, 0x00, 0x01])

    @property
    def body(self) -> bytearray:
        """Return the query body including its inner CRC."""
        body = bytearray([self.body_type]) + self._body
        body.append(calculate(body))
        return body


def supports_ac_c1_frequency(
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether an appliance exposes frequency through C1 group 0x41.

    Returns
    -------
    ``True`` when the model/subtype exposes the C1 diagnostics group.

    """
    if device_type != _AC_DEVICE_TYPE or subtype is None:
        return False
    return (str(model), int(subtype)) in SUPPORTED_AC_C1_FREQUENCY_MODELS


def supports_ac_diagnostic_attribute(
    attribute: str,
    device_type: int,
    model: str,
    subtype: int | None,
) -> bool:
    """Return whether a model supports an integration-level AC diagnostic.

    Returns
    -------
    ``True`` when the requested attribute is supported for the model/subtype.

    """
    if attribute in AC_C1_DIAGNOSTIC_ATTRIBUTES and (
        supports_ac_c1_frequency(device_type, model, subtype)
    ):
        return True
    return supports_ac_bb_diagnostic_attribute(
        attribute,
        device_type,
        model,
        subtype,
    )


def install_ac_c1_diagnostics(device: MideaDevice) -> None:
    """Install the model-specific group query and response parser."""
    if not supports_ac_c1_frequency(
        device.device_type,
        device.model,
        device.subtype,
    ):
        return

    attributes = cast("dict[str, Any]", vars(device)["_attributes"])
    attributes.update(dict.fromkeys(AC_C1_DIAGNOSTIC_ATTRIBUTES))
    original_build_query = device.build_query
    original_process_message = device.process_message

    def build_query() -> list[Any]:
        queries = original_build_query()
        protocol_version = cast("int", vars(device)["_message_protocol_version"])
        return [*queries, _MessageGroupOneQuery(protocol_version)]

    def process_message(message: bytes) -> dict[str, Any]:
        status = original_process_message(message)
        if (
            len(message) > _TARGET_FREQUENCY_OFFSET
            and message[_MESSAGE_BODY_OFFSET] == _C1_BODY_TYPE
            and message[_GROUP_TYPE_OFFSET] == _GROUP_ONE_TYPE
        ):
            frequency = int(message[_ACTUAL_FREQUENCY_OFFSET])
            target_frequency = int(message[_TARGET_FREQUENCY_OFFSET])
            attributes[COMPRESSOR_FREQUENCY] = frequency
            attributes[COMPRESSOR_TARGET_FREQUENCY] = target_frequency
            status[COMPRESSOR_FREQUENCY] = frequency
            status[COMPRESSOR_TARGET_FREQUENCY] = target_frequency
            _LOGGER.debug(
                "[%s] C1 compressor diagnostics: actual=%s Hz, target=%s Hz",
                device.device_id,
                frequency,
                target_frequency,
            )
        return status

    device.build_query = build_query  # type: ignore[method-assign]
    device.process_message = process_message  # type: ignore[method-assign]
