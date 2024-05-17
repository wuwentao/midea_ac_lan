from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
)


class MessageCDBase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xCD,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageCDBase):
    def __init__(self,protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageSet(MessageCDBase):
    def __init__(self,protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x01)
        self.power = False
        self.target_temperature = 0
        self.aux_heating = False
        self.fields = {}
        self.mode = 1

    def read_field(self, field):
        value = self.fields.get(field, 0)
        return value if value else 0

    @property
    def _body(self):
        power = 0x01 if self.power else 0x00
        mode = self.mode + 1
        target_temperature = round(self.target_temperature * 2 + 30)
        return bytearray([
            0x01, power, mode, target_temperature,
            self.read_field("trValue"),
            self.read_field("openPTC"),
            self.read_field("ptcTemp"),
            0  # self.read_field("byte8")
        ])


class CDGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[2] & 0x01) > 0
        self.target_temperature = round((body[3] - 30) / 2)
        if (body[2] & 0x02) > 0:
            self.mode = 0
        elif (body[2] & 0x04) > 0:
            self.mode = 1
        elif (body[2] & 0x08) > 0:
            self.mode = 2
        self.current_temperature = round((body[4] - 30) / 2)
        self.condenser_temperature = (body[7] - 30) / 2
        self.outdoor_temperature = (body[8] - 30) / 2
        self.compressor_temperature = (body[9] - 30) / 2
        self.max_temperature = round((body[10] - 30) / 2)
        self.min_temperature = round((body[11] - 30) / 2)
        self.compressor_status = (body[27] & 0x08) > 0
        if (body[28] & 0x20) > 0:
            self.mode = 3

class CD02MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.fields = {}
        self.power = (body[2] & 0x01) > 0
        self.mode = body[3]
        self.target_temperature = round((body[4] - 30) / 2)
        self.fields["trValue"] = body[5]
        self.fields["openPTC"] = body[5]
        self.fields["ptcTemp"] = body[7]
        self.fields["byte8"] = body[8]


class MessageCDResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.query, MessageType.notify2]:
            self.set_body(CDGeneralMessageBody(super().body))
        elif self.message_type == MessageType.set and self.body_type == 0x01:
            self.set_body(CD02MessageBody(super().body))
        self.set_attr()
