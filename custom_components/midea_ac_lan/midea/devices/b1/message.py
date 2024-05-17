from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageB1Base(MessageRequest):
    def __init__(self, protocol_version, message_type,  body_type):
        super().__init__(
            device_type=0xB1,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageB1Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x00)

    @property
    def _body(self):
        return bytearray([])


class B1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.door = (body[16] & 0x02) > 0
        self.status = body[1]
        self.time_remaining = (0 if body[6] == 0xFF else body[6]) * 3600 + \
                              (0 if body[7] == 0xFF else body[7]) * 60 + \
                              (0 if body[8] == 0xFF else body[8])
        self.current_temperature = body[19]
        self.tank_ejected = (body[16] & 0x04) > 0
        self.water_shortage = (body[16] & 0x08) > 0
        self.water_change_reminder = (body[16] & 0x10) > 0


class MessageB1Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.notify1, MessageType.query]:
            self.set_body(B1MessageBody(super().body))
        self.set_attr()

