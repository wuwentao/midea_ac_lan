from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageE8Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xE8,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageE8Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0xAA)

    @property
    def _body(self):
        return bytearray([0x55, 0x00, 0x01, 0x00, 0x00])


class E8MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.status = body[11]
        self.time_remaining = body[16] * 3600 + body[17] * 60 + body[18]
        self.keep_warm_remaining = body[19] * 3600 + body[20] * 60 + body[21]
        self.working_time = body[28] * 3600 + body[29] * 60 + body[30]
        self.target_temperature = body[39]
        self.current_temperature = body[39]
        self.finished = (body[41] & 0x01) > 0
        self.water_shortage = body[43] > 0


class MessageE8Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if len(super().body) > 6:
            sub_cmd = super().body[6]
            if ((self.message_type == MessageType.set and sub_cmd in [0x02, 0x04, 0x06]) or
                    self.message_type in [MessageType.query, MessageType.notify1] and sub_cmd ==2):
                self.set_body(E8MessageBody(super().body))
        self.set_attr()

