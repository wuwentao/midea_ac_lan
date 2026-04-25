"""Fix oscillate for 56011CEC-like fans.

These fans report oscillate state at body[51] instead of body[8]
and expect oscillate command at body[50] instead of body[7].
"""

from __future__ import annotations

from midealocal.devices.fa.message import FAGeneralMessageBody, MessageSet

OSCILLATE_GET_BYTE = 51
OSCILLATE_SET_BYTE = 50
OSCILLATE_ON_VALUE = 0xFE

_orig_body_init = FAGeneralMessageBody.__init__


def _patched_body_init(
    self: FAGeneralMessageBody,
    body: bytearray,
) -> None:
    _orig_body_init(self, body)
    # For 56011CEC-like fans: oscillate state is at body[51] with value 0xFE
    if (
        len(body) > OSCILLATE_GET_BYTE
        and body[OSCILLATE_GET_BYTE] == OSCILLATE_ON_VALUE
    ):
        self.oscillate = True


FAGeneralMessageBody.__init__ = _patched_body_init  # type: ignore[method-assign]

_orig_body_prop = MessageSet._body.fget  # noqa: SLF001


def _patched_body_prop(self: MessageSet) -> bytearray:
    result = _orig_body_prop(self)  # type: ignore[misc]
    if self.oscillate is not None:
        while len(result) <= OSCILLATE_SET_BYTE:
            result.append(0x00)
        result[OSCILLATE_SET_BYTE] = OSCILLATE_ON_VALUE if self.oscillate else 0x00
    return result


MessageSet._body = property(_patched_body_prop)  # noqa: SLF001
