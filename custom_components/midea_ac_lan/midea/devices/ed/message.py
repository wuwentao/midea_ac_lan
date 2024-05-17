from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class NewSetTags(IntEnum):
    power = 0x0100
    lock = 0x0201


class EDNewSetParamPack:
    @staticmethod
    def pack(param, value, addition=0):
        return bytearray([param & 0xFF, param >> 8, value, addition & 0xFF, addition >> 8])


class MessageEDBase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xED,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageEDBase):
    def __init__(self, protocol_version, device_class):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=device_class)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageNewSet(MessageEDBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x15)
        self.power = None
        self.lock = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x01, 0x00])
        if self.power is not None:
            pack_count += 1
            payload.extend(
                EDNewSetParamPack.pack(
                    param=NewSetTags.power,  # power
                    value=0x01 if self.power else 0x00
                )
            )
        if self.lock is not None:
            pack_count += 1
            payload.extend(
                EDNewSetParamPack.pack(
                    param=NewSetTags.lock,  # lock
                    value=0x01 if self.lock else 0x00
                )
            )
        payload[1] = pack_count
        return payload


class MessageOldSet(MessageEDBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=None)

    @property
    def body(self):
        return bytearray([])

    @property
    def _body(self):
        return bytearray([])


class EDMessageBody01(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.water_consumption = body[7] + (body[8] << 8)
        self.in_tds = body[36] + (body[37] << 8)
        self.out_tds = body[38] + (body[39] << 8)
        self.child_lock = body[15] > 0
        self.filter1 = round((body[25] + (body[26] << 8)) / 24)
        self.filter2 = round((body[27] + (body[28] << 8)) / 24)
        self.filter3 = round((body[29] + (body[30] << 8)) / 24)
        self.life1 = body[16]
        self.life2 = body[17]
        self.life3 = body[18]


class EDMessageBody03(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[51] & 0x01) > 0
        self.child_lock = (body[51] & 0x08) > 0
        self.water_consumption = body[20] + (body[21] << 8)
        self.life1 = body[22]
        self.life2 = body[23]
        self.life3 = body[24]
        self.in_tds = body[27] + (body[28] << 8)
        self.out_tds = body[29] + (body[30] << 8)


class EDMessageBody05(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[51] & 0x01) > 0
        self.child_lock = (body[51] & 0x08) > 0
        self.water_consumption = body[20] + (body[21] << 8)


class EDMessageBody06(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[51] & 0x01) > 0
        self.child_lock = (body[51] & 0x08) > 0
        self.water_consumption = body[25] + (body[26] << 8)


class EDMessageBody07(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.water_consumption = (body[21] << 8) + body[20]
        self.power = (body[51] & 0x01) > 0
        self.child_lock = (body[51] & 0x08) > 0


class EDMessageBodyFF(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        data_offset = 2
        while True:
            length = (body[data_offset + 2] >> 4) + 2
            attr = ((body[data_offset + 2] % 16) << 8) + body[data_offset + 1]
            if attr == 0x000:
                self.child_lock = (body[data_offset + 5] & 0x01) > 0
                self.power = (body[data_offset + 6] & 0x01) > 0
            elif attr == 0x011:
                self.water_consumption = float((body[data_offset + 3] +
                                                (body[data_offset + 4] << 8) +
                                                (body[data_offset + 5] << 16) +
                                                (body[data_offset + 6] << 24))) / 1000
            elif attr == 0x013:
                self.in_tds = body[data_offset + 3] + (body[data_offset + 4] << 8)
                self.out_tds = body[data_offset + 5] + (body[data_offset + 6] << 8)
            elif attr == 0x10:
                self.life1 = body[data_offset + 3]
                self.life2 = body[data_offset + 4]
                self.life3 = body[data_offset + 5]
            # fix index out of range error
            if data_offset + length + 6 > len(body):
                break
            data_offset += length


class MessageEDResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self._message_type in [MessageType.query, MessageType.notify1]:
            self.device_class = self._body_type
            if self._body_type in [0x00, 0xFF]:
                self.set_body(EDMessageBodyFF(super().body))
            if self.body_type == 0x01:
                self.set_body(EDMessageBody01(super().body))
            elif self.body_type in [0x03, 0x04]:
                self.set_body(EDMessageBody03(super().body))
            elif self.body_type == 0x05:
                self.set_body(EDMessageBody05(super().body))
            elif self.body_type == 0x06:
                self.set_body(EDMessageBody06(super().body))
            elif self.body_type == 0x07:
                self.set_body(EDMessageBody07(super().body))
        self.set_attr()
