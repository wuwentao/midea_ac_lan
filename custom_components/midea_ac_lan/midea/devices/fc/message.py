from ...core.crc8 import calculate
from ...core.message import MessageBody, MessageRequest, MessageResponse, MessageType


class MessageFCBase(MessageRequest):
    _message_serial = 0

    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xFC,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )
        MessageFCBase._message_serial += 1
        if MessageFCBase._message_serial >= 254:
            MessageFCBase._message_serial = 1
        self._message_id = MessageFCBase._message_serial

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body + bytearray([self._message_id])
        body.append(calculate(body))
        return body


class MessageQuery(MessageFCBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x41,
        )

    @property
    def _body(self):
        return bytearray(
            [
                0x00,
                0x00,
                0xFF,
                0x03,
                0x00,
                0x00,
                0x02,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )


class MessageSet(MessageFCBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x48,
        )
        self.power = False
        self.mode = 0
        self.fan_speed = 0
        self.child_lock = False
        self.prompt_tone = False
        self.anion = False
        self.standby = False
        self.screen_display = 0
        self.detect_mode = 0
        self.standby_detect = [40, 20]

    @property
    def _body(self):
        # byte1 power
        power = 0x01 if self.power else 0x00
        detect = 0x08 if self.detect_mode > 0 else 0x00
        detect_mode = (self.detect_mode - 1) if self.detect_mode > 0 else 0
        # byte2 mode
        # byte3 fan_speed
        # byte 8 child_lock
        child_lock = 0x80 if self.child_lock else 0x00
        # byte 9 anion
        anion = 0x20 if self.anion else 0x00
        # byte 10 prompt_tone
        prompt_tone = 0x40 if self.prompt_tone else 0x00
        # byte 15/16/17 standby
        if self.standby:
            standby = 0x04
            standby_detect_high = self.standby_detect[0]
            standby_detect_low = self.standby_detect[1]
        else:
            standby = 0x08
            standby_detect_high = 0
            standby_detect_low = 0
        return bytearray(
            [
                power | prompt_tone | detect | 0x02,
                self.mode,
                self.fan_speed,
                0x00,
                0x00,
                0x00,
                0x00,
                child_lock,
                self.screen_display,
                anion,
                0x00,
                0x00,
                0x00,
                detect_mode,
                standby,
                standby_detect_high,
                standby_detect_low,
                0x00,
                0x00,
                0x00,
            ]
        )


class FCGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x01) > 0
        self.mode = body[2] & 0xF0
        self.fan_speed = body[3] & 0x7F
        self.screen_display = body[9] & 0x07
        if len(body) > 14 and body[14] != 0xFF:
            self.pm25 = body[13] + (body[14] << 8)
        else:
            self.pm25 = None
        if len(body) > 15 and body[15] != 0xFF:
            self.tvoc = body[15]
        else:
            self.tvoc = None
        self.anion = (body[19] & 0x40 > 0) if len(body) > 19 else False
        self.standby = ((body[34] & 0xFF) == 0x14) if len(body) > 34 else False
        self.child_lock = (body[8] & 0x80 > 0) if len(body) > 8 else False
        if len(body) > 23:
            self.filter1_life = body[23]
        if len(body) > 24:
            self.filter2_life = body[24]
        if len(body) > 29:
            if (body[1] & 0x08) > 0:
                self.detect_mode = body[29] + 1
            else:
                self.detect_mode = 0
        if len(body) > 38 and body[38] != 0xFF:
            self.hcho = body[37] + (body[38] << 8)
        else:
            self.hcho = None


class FCNotifyMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x01) > 0
        self.mode = body[2] & 0xF0
        self.fan_speed = body[3] & 0x7F
        self.screen_display = body[9] & 0x07
        if len(body) > 14 and body[14] != 0xFF:
            self.pm25 = body[13] + (body[14] << 8)
        else:
            self.pm25 = None
        if len(body) > 15 and body[15] != 0xFF:
            self.tvoc = body[15]
        else:
            self.tvoc = None
        self.anion = (body[10] & 0x20 > 0) if len(body) > 10 else False
        self.standby = (body[27] & 0x14 == 0xFF) if len(body) > 27 else False
        self.child_lock = (body[10] & 0x10 > 0) if len(body) > 10 else False
        if len(body) > 22:
            if (body[1] & 0x08) > 0:
                self.detect_mode = body[22] + 1
            else:
                self.detect_mode = 0
        if len(body) > 31 and body[31] != 0xFF:
            self.hcho = body[30] + (body[31] << 8)
        else:
            self.hcho = None


class MessageFCResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.body_type in [0xB0, 0xB1]:
            pass
        else:
            if (
                self.message_type
                in [MessageType.query, MessageType.set, MessageType.notify1]
                and self.body_type == 0xC8
            ):
                self.set_body(FCGeneralMessageBody(super().body))
            elif self.message_type == MessageType.notify1 and self.body_type == 0xA0:
                self.set_body(FCNotifyMessageBody(super().body))
        self.set_attr()
