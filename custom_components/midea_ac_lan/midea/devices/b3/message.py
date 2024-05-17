from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageB3Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xB3,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageB3Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x31)

    @property
    def _body(self):
        return bytearray([])


class B3MessageBody31(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.top_compartment_status = body[1]
        self.top_compartment_mode = body[2]
        self.top_compartment_temperature = body[3]
        self.top_compartment_remaining = (
            body[23] * 3600 if len(body) > 23 and body[23] != 0xFF else 0 +
            body[4] * 60 if body[4] != 0xFF else 0 +
            body[5] if body[5] != 0xFF else 0
        )
        self.bottom_compartment_status = body[6]
        self.bottom_compartment_mode = body[7]
        self.bottom_compartment_temperature = body[8]
        self.bottom_compartment_remaining = (
            body[24] * 3600 if len(body) > 24 and body[24] != 0xFF else 0 +
            body[9] * 60 if body[9] != 0xFF else 0 +
            body[10] if body[10] != 0xFF else 0
        )
        self.middle_compartment_status = body[17]
        self.middle_compartment_mode = body[18]
        self.middle_compartment_temperature = body[19]
        self.middle_compartment_remaining = (
            body[25] * 3600 if len(body) > 25 and body[25] != 0xFF else 0 +
            body[20] * 60 if body[20] != 0xFF else 0 +
            body[21] if body[21] != 0xFF else 0
        )
        self.lock = body[11] & 0x01 > 0
        self.bottom_compartment_door = body[11] & 0x02 > 0
        self.top_compartment_door = body[11] & 0x04 > 0
        self.middle_compartment_door = body[11] & 0x10 > 0
        self.bottom_compartment_preheating = body[16] & 0x01 > 0
        self.top_compartment_preheating = body[16] & 0x02 > 0
        self.middle_compartment_preheating = body[16] & 0x10 > 0
        self.bottom_compartment_cooling = body[16] & 0x04 > 0
        self.top_compartment_cooling = body[16] & 0x08 > 0
        self.middle_compartment_cooling = body[16] & 0x20 > 0


class B3MessageBody21(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.top_compartment_status = body[1]
        self.top_compartment_mode = body[2]
        self.top_compartment_temperature = body[3]
        self.top_compartment_remaining = (
            body[17] * 3600 if len(body) > 17 and body[17] != 0xFF else 0 +
            body[4] * 60 if body[4] != 0xFF else 0 +
            body[5] if body[5] != 0xFF else 0
        )
        self.bottom_compartment_status = body[6]
        self.bottom_compartment_mode = body[7]
        self.bottom_compartment_temperature = body[8]
        self.bottom_compartment_remaining = (
            body[18] * 3600 if len(body) > 18 and body[18] != 0xFF else 0 +
            body[9] * 60 if body[9] != 0xFF else 0 +
            body[10] if body[10] != 0xFF else 0
        )
        self.middle_compartment_status = body[12]
        self.middle_compartment_mode = body[13]
        self.middle_compartment_temperature = body[14]
        self.middle_compartment_remaining = (
            body[19] * 3600 if len(body) > 19 and body[19] != 0xFF else 0 +
            body[15] * 60 if body[15] != 0xFF else 0 +
            body[16] if body[16] != 0xFF else 0
        )
        self.lock = body[11] & 0x01 > 0


class B3MessageBody24(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.top_compartment_status = body[5]
        self.top_compartment_mode = body[6]
        self.top_compartment_temperature = body[7]
        self.top_compartment_remaining = (
            body[8] * 60 if body[8] != 0xFF else 0 +
            body[9] if body[9] != 0xFF else 0
        )
        self.bottom_compartment_status = body[10]
        self.bottom_compartment_mode = body[11]
        self.bottom_compartment_temperature = body[12]
        self.bottom_compartment_remaining = (
            body[13] * 60 if body[13] != 0xFF else 0 +
            body[14] if body[14] != 0xFF else 0
        )
        self.bottom_compartment_status = body[15]
        self.bottom_compartment_mode = body[16]
        self.bottom_compartment_temperature = body[17]
        self.bottom_compartment_remaining = (
            body[18] * 60 if body[18] != 0xFF else 0 +
            body[19] if body[19] != 0xFF else 0
        )


class MessageB3Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if (self.message_type == MessageType.query and self.body_type == 0x31 or
                self.message_type == MessageType.notify1 and self.body_type == 0x41):
            self.set_body(B3MessageBody31(super().body))
        elif self.message_type == MessageType.set and self.body_type == 0x21:
            self.set_body(B3MessageBody21(super().body))
        elif self.message_type == MessageType.set and self.body_type == 0x24:
            self.set_body(B3MessageBody21(super().body))
        self.set_attr()

