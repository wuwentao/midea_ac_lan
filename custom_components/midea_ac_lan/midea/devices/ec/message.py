from ...core.message import (MessageBody, MessageRequest, MessageResponse,
                             MessageType)


class MessageECBase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xEC,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageECBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=None,
        )

    @property
    def body(self):
        return bytearray([0xAA, 0x55, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    @property
    def _body(self):
        return bytearray([])


class ECGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.mode = body[4] + (body[5] << 8)
        self.progress = body[8]
        self.cooking = self.progress == 1
        self.time_remaining = body[12] * 60 + body[13]
        self.keep_warm_time = body[16] * 60 + body[17]
        self.top_temperature = body[21]
        self.bottom_temperature = body[22]
        self.with_pressure = (body[23] & 0x04) > 0


class ECBodyNew(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.progress = body[11]
        self.cooking = self.progress == 1
        self.time_remaining = body[16] * 60 + body[17]
        self.keep_warm_time = body[19] * 60 + body[20]
        self.top_temperature = body[48]
        self.bottom_temperature = body[49]
        self.with_pressure = body[33] > 0


class MessageECResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type == MessageType.notify1 and super().body[3] == 0x01:
            self.set_body(ECBodyNew(super().body))
        elif (
            (self.message_type == MessageType.set and super().body[3] == 0x02)
            or (self.message_type == MessageType.query and super().body[3] == 0x03)
            or (self.message_type == MessageType.notify1 and super().body[3] == 0x04)
            or (self.message_type == MessageType.notify1 and super().body[3] == 0x3D)
        ):
            self.set_body(ECGeneralMessageBody(super().body))
        elif self.message_type == MessageType.notify1 and super().body[3] == 0x06:
            self.mode = super().body[4] + (super().body[5] << 8)
        self.set_attr()
