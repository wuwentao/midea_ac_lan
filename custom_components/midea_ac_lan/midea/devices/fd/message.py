from ...core.crc8 import calculate
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageFDBase(MessageRequest):
    _message_serial = 0

    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xFD,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )
        MessageFDBase._message_serial += 1
        if MessageFDBase._message_serial >= 254:
            MessageFDBase._message_serial = 1
        self._message_id = MessageFDBase._message_serial

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body + bytearray([self._message_id])
        body.append(calculate(body))
        return body


class MessageQuery(MessageFDBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x03,
            0x00, 0x00, 0x02, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00
        ])


class MessageSet(MessageFDBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x48)
        self.power = False
        self.fan_speed = 0
        self.target_humidity = 50
        self.prompt_tone = False
        self.screen_display = 0x07
        self.mode = 0x01
        self.disinfect = None

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        prompt_tone = 0x40 if self.prompt_tone else 0x00
        disinfect = 0 if self.disinfect is None else (1 if self.disinfect else 2)
        return bytearray([
            power | prompt_tone | 0x02,
            0x00,
            self.fan_speed,
            0x00, 0x00, 0x00,
            self.target_humidity,
            0x00,
            self.screen_display,
            self.mode,
            0x00, 0x00, 0x00, 0x00,
            disinfect,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00
        ])


class FDC8MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x01) > 0
        self.fan_speed = body[3] & 0x7F
        self.target_humidity = body[7]
        self.current_humidity = body[16]
        self.current_temperature = (body[17] - 50) / 2
        self.tank = body[10]
        self.mode = (body[8] & 0x70) >> 4
        self.screen_display = body[9] & 0x07
        if len(body) > 36:
            disinfect = body[34] & 0x03
            if disinfect == 1:
                self.disinfect = True
            elif disinfect == 2:
                self.disinfect = False


class FDA0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x01) > 0
        self.fan_speed = body[3] & 0x7F
        self.target_humidity = body[7]
        self.current_humidity = body[16]
        self.current_temperature = (body[17] - 50) / 2
        self.tank = body[10]
        self.mode = body[10] & 0x07
        self.screen_display = body[9] & 0x07
        if len(body) > 29:
            disinfect = body[27] & 0x03
            if disinfect == 1:
                self.disinfect = True
            elif disinfect == 2:
                self.disinfect = False


class MessageFDResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.query, MessageType.set, MessageType.notify1]:
            if self.body_type in [0xB0, 0xB1]:
                pass
            elif self.body_type == 0xA0:
                self.set_body(FDA0MessageBody(super().body))
            elif self.body_type == 0xC8:
                self.set_body(FDC8MessageBody(super().body))
        self.set_attr()
        if hasattr(self, "fan_speed") and self.fan_speed is not None and self.fan_speed < 5:
            self.fan_speed = 1
