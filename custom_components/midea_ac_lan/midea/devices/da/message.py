from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageDABase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xDA,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageDABase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x03)

    @property
    def _body(self):
        return bytearray([])


class MessagePower(MessageDABase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x02)
        self.power = False

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        return bytearray([
            power, 0xFF
        ])


class MessageStart(MessageDABase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x02)
        self.start = False
        self.washing_data = bytearray([])

    @property
    def _body(self):
        if self.start:
            return bytearray([
                0xFF, 0x01
            ]) + self.washing_data
        else:
            # Stop
            return bytearray([
                0xFF, 0x00
            ])


class DAGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = body[1] > 0
        self.start = True if body[2] in [2, 6] else False
        self.error_code = body[24]
        self.program = body[4]
        self.wash_time = body[9]
        self.soak_time = body[12]
        self.dehydration_time = (body[10] & 0xf0) >> 4
        self.dehydration_speed = (body[6] & 0xf0) >> 4
        self.rinse_count = body[10] & 0xf
        self.rinse_level = (body[5] & 0xf0) >> 4
        self.wash_level = body[5] & 0xf
        self.wash_strength = body[6] & 0xf
        self.softener = (body[8] & 0xf0) >> 4
        self.detergent = body[8] & 0x0f
        self.washing_data = body[3:15]
        self.progress = 0
        for i in range(1, 7):
            if (body[16] & (1 << i)) > 0:
                self.progress = i
                break
        if self.power:
            self.time_remaining = body[17] + body[18] * 60
        else:
            self.time_remaining = None


class MessageDAResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.query, MessageType.set] or \
                (self.message_type == MessageType.notify1 and self.body_type == 0x04):
            self.set_body(DAGeneralMessageBody(super().body))
        self.set_attr()
