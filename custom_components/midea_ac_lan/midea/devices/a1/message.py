from enum import IntEnum

from ...core.crc8 import calculate
from ...core.message import (
    MessageBody,
    MessageRequest,
    MessageResponse,
    MessageType,
    NewProtocolMessageBody,
)


class NewProtocolTags(IntEnum):
    light = 0x005B


class MessageA1Base(MessageRequest):
    _message_serial = 0

    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xA1,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )
        MessageA1Base._message_serial += 1
        if MessageA1Base._message_serial >= 100:
            MessageA1Base._message_serial = 1
        self._message_id = MessageA1Base._message_serial

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body + bytearray([self._message_id])
        body.append(calculate(body))
        return body


class MessageQuery(MessageA1Base):
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
                0x81,
                0x00,
                0xFF,
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
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )


class MessageNewProtocolQuery(MessageA1Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0xB1,
        )

    @property
    def _body(self):
        query_params = [NewProtocolTags.light]
        _body = bytearray([len(query_params)])
        for param in query_params:
            _body.extend([param & 0xFF, param >> 8])
        return _body


class MessageSet(MessageA1Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x48,
        )
        self.power = False
        self.prompt_tone = False
        self.mode = 1
        self.fan_speed = 40
        self.child_lock = False
        self.target_humidity = 40
        self.swing = False
        self.anion = False
        self.water_level_set = 50

    @property
    def _body(self):
        # byte1, power, prompt_tone
        power = 0x01 if self.power else 0x00
        prompt_tone = 0x40 if self.prompt_tone else 0x00
        # byte2 mode
        mode = self.mode
        # byte3 fan_speed
        fan_speed = self.fan_speed
        # byte7 target_humidity
        target_humidity = self.target_humidity
        # byte8 child_lock
        child_lock = 0x80 if self.child_lock else 0x00
        # byte9 anion
        anion = 0x40 if self.anion else 0x00
        # byte10 swing
        swing = 0x08 if self.swing else 0x00
        # byte 13 water_level_set
        water_level_set = self.water_level_set
        return bytearray(
            [
                power | prompt_tone | 0x02,
                mode,
                fan_speed,
                0x00,
                0x00,
                0x00,
                target_humidity,
                child_lock,
                anion,
                swing,
                0x00,
                0x00,
                water_level_set,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )


class MessageNewProtocolSet(MessageA1Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0xB0,
        )
        self.light = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x00])
        if self.light is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.light,
                    value=bytearray([0x01 if self.light else 0x00]),
                )
            )
        payload[0] = pack_count
        return payload


class A1GeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x01) > 0
        self.mode = body[2] & 0x0F
        self.fan_speed = body[3] & 0x7F
        self.target_humidity = 35 if (body[7] < 35) else body[7]
        self.child_lock = (body[8] & 0x80) > 0
        self.anion = (body[9] & 0x40) > 0
        self.tank = body[10] & 0x7F
        self.water_level_set = body[15]
        self.current_humidity = body[16]
        self.current_temperature = (body[17] - 50) / 2
        self.swing = (body[19] & 0x20) > 0
        if self.fan_speed < 5:
            self.fan_speed = 1


class A1NewProtocolMessageBody(NewProtocolMessageBody):
    def __init__(self, body, bt):
        super().__init__(body, bt)
        params = self.parse()
        if NewProtocolTags.light in params:
            self.light = params[NewProtocolTags.light][0] > 0


class MessageA1Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [
            MessageType.query,
            MessageType.set,
            MessageType.notify1,
        ]:
            if self.body_type in [0xB0, 0xB1, 0xB5]:
                self.set_body(A1NewProtocolMessageBody(super().body, self.body_type))
            else:
                self.set_body(A1GeneralMessageBody(super().body))
        elif self.message_type == MessageType.notify2 and self.body_type == 0xA0:
            self.set_body(A1GeneralMessageBody(super().body))
        self.set_attr()
