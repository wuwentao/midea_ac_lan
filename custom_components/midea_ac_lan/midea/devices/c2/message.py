from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class C2MessageEnum(IntEnum):
    sensor_light = 0x01
    child_lock = 0x10
    foam_shield = 0x1F
    water_temp_level = 0x09
    seat_temp_level = 0x0a
    dry_level = 0x0c


C2_MESSAGE_KEYS = {
    C2MessageEnum.child_lock: {True: 0x01 << 4, False: 0x00},
    C2MessageEnum.sensor_light: {True: 0x01 << 1, False: 0x00},
    C2MessageEnum.foam_shield: {True: 0x01 << 2, False: 0x00},
    C2MessageEnum.dry_level: {0: 0x00, 1: 0x01 << 1, 2: 0x02 << 1, 3: 0x03 << 1},
    C2MessageEnum.seat_temp_level: {0: 0x00, 1: 0x01 << 3, 2: 0x02 << 3, 3: 0x03 << 3, 4: 0x04 << 3, 5: 0x05 << 3},
    C2MessageEnum.water_temp_level: {0: 0x00, 1: 0x01, 2: 0x02, 3: 0x03, 4: 0x04, 5: 0x05}
}


class MessageC2Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xC2,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageC2Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessagePower(MessageC2Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x00)
        self.power = False
    @property
    def _body(self):
        if self.power:
            self.body_type = 0x01
        else:
            self.body_type = 0x02
        return bytearray([0x01])


class MessagePowerOff(MessageC2Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x02)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageSet(MessageC2Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x00)

        self.child_lock = None
        self.sensor_light = None
        self.water_temp_level = None
        self.seat_temp_level = None
        self.dry_level = None
        self.foam_shield = None

    @property
    def _body(self):
        self.body_type = 0x14
        key = 0x00
        value = 0x00
        if self.child_lock is not None:
            key = C2MessageEnum.child_lock
            value = self.child_lock
        elif self.sensor_light is not None:
            key = C2MessageEnum.sensor_light
            value = self.sensor_light
        elif self.water_temp_level is not None:
            key = C2MessageEnum.water_temp_level
            value = self.water_temp_level
        elif self.seat_temp_level is not None:
            key = C2MessageEnum.seat_temp_level
            value = self.seat_temp_level
        elif self.dry_level is not None:
            key = C2MessageEnum.dry_level
            value = self.dry_level
        elif self.foam_shield is not None:
            key = C2MessageEnum.foam_shield
            value = self.foam_shield
        value = C2_MESSAGE_KEYS.get(key).get(value)
        return bytearray([key, value])


class C2MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.seat_status = (body[3] & 0x01) > 0
        self.dry_level = ((body[6] & 0x7E) >> 1)
        self.water_temp_level = (body[9] & 0x07)
        self.seat_temp_level = ((body[9] & 0x38) >> 3)
        self.lid_status = (body[12] & 0x40) > 0
        self.foam_shield = (body[13] & 0x80) > 0
        self.sensor_light = (body[14] & 0x01) > 0
        self.light_status = (body[14] & 0x02) > 0
        self.child_lock = (body[14] & 0x04) > 0
        self.water_temperature = body[11]
        self.seat_temperature = body[11]
        self.filter_life = 100 - body[19]


class C2Notify1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)


class MessageC2Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.notify1, MessageType.query, MessageType.set]:
            self.set_body(C2MessageBody(super().body))
        self.set_attr()
