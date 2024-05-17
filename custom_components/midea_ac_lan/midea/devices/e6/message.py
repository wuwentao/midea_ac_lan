from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageE6Base(MessageRequest):
    def __init__(self, protocol_version, message_type):
        super().__init__(
            device_type=0xE6,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=None
        )

    @property
    def body(self):
        return self._body

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageE6Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query
        )

    @property
    def _body(self):
        return bytearray([0x01, 0x01] + [0] * 28)


class MessageSet(MessageE6Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set
        )
        self.main_power = None
        self.heating_temperature = None
        self.bathing_temperature = None
        self.heating_power = None

    @property
    def _body(self):
        body = []
        if self.main_power is not None:
            main_power = 0x01 if self.main_power else 0x02
            body = [main_power, 0x01]
        elif self.heating_temperature is not None:
            body = [0x04, 0x13, self.heating_temperature]
        elif self.bathing_temperature is not None:
            body = [0x04, 0x12, self.bathing_temperature]
        elif self.heating_power is not None:
            heating_power = 0x01 if self.heating_power else 0x02
            body = [0x04, 0x01, heating_power]
        body_len = len(body)
        return bytearray(body + [0] * (30 - body_len))


class E6GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.main_power = (body[2] & 0x04) > 0
        self.heating_working = (body[2] & 0x10) > 0
        self.bathing_working = (body[2] & 0x20) > 0
        self.heating_power = (body[4] & 0x01) > 0
        self.min_temperature = [
            body[16],
            body[11]
        ]
        self.max_temperature = [
            body[15],
            body[10]
        ]
        self.heating_temperature = body[17]
        self.bathing_temperature = body[12]
        self.heating_leaving_temperature = body[14]
        self.bathing_leaving_temperature = body[8]


class MessageE6Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        self.set_body(E6GeneralMessageBody(super().body))
        self.set_attr()
