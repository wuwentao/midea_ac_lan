from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageBFBase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xBF,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageBFBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageBFBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x02)
        self.power = None
        self.child_lock = None

    @property
    def _body(self):
        power = 0xFF if self.power is None else 0x11 if self.power else 0x01
        child_lock = 0xFF if self.child_lock is None else 0x01 if self.child_lock else 0x00
        return bytearray([power, child_lock] + [0xFF] * 7)


class MessageBFBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.status = body[31]
        self.time_remaining = (0 if body[22] == 0xFF else body[22]) * 3600 + \
                              (0 if body[23] == 0xFF else body[23]) * 60 + \
                              (0 if body[24] == 0xFF else body[24])
        cur_temperature = body[25] * 256 + body[26]
        if cur_temperature == 0:
            cur_temperature = body[27] * 256 + body[28]
        self.current_temperature = cur_temperature
        self.child_lock = (body[32] & 0x01) > 0
        self.door = (body[32] & 0x02) > 0
        self.tank_ejected = (body[32] & 0x04) > 0
        self.water_state = (body[32] & 0x08) > 0
        self.water_change_reminder = (body[32] & 0x10) > 0


class MessageBFResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.set, MessageType.notify1, MessageType.query] and self.body_type == 0x01:
            self.set_body(MessageBFBody(super().body))
        self.set_attr()
