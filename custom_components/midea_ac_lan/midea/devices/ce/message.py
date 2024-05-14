from ...core.message import MessageBody, MessageRequest, MessageResponse, MessageType


class MessageFABase(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xCE,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageFABase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01,
        )

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageFABase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x01,
        )

        self.power = False
        self.fan_speed = 0
        self.link_to_ac = False
        self.sleep_mode = False
        self.eco_mode = False
        self.aux_heating = False
        self.powerful_purify = False
        self.scheduled = False
        self.child_lock = False

    @property
    def _body(self):
        power = 0x80 if self.power else 0x00
        link_to_ac = 0x01 if self.link_to_ac else 0x00
        sleep_mode = 0x02 if self.sleep_mode else 0x00
        eco_mode = 0x04 if self.eco_mode else 0x00
        aux_heating = 0x08 if self.aux_heating else 0x00
        powerful_purify = 0x10 if self.powerful_purify else 0x00
        scheduled = 0x01 if self.scheduled else 0x00
        child_lock = 0x7F if self.child_lock else 0x00
        return bytearray(
            [
                power | 0x01,
                self.fan_speed,
                link_to_ac | sleep_mode | eco_mode | aux_heating | powerful_purify,
                scheduled,
                0x00,
                child_lock,
            ]
        )


class CEGeneralMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x80) > 0
        self.child_lock = (body[1] & 0x20) > 0
        self.scheduled = (body[1] & 0x40) > 0
        self.fan_speed = body[2]
        self.pm25 = (body[3] << 8) + body[4]
        self.co2 = (body[5] << 8) + body[6]
        if body[7] != 0xFF:
            self.current_humidity = (body[7] << 8) + body[8] / 10
        else:
            self.current_humidity = None
        if body[9] != 0xFF:
            self.current_temperature = (body[9] << 8) + (body[10] - 60) / 2
        else:
            self.current_temperature = None
        if body[11] != 0xFF:
            self.hcho = (body[11] << 8) + body[12] / 1000
        else:
            self.hcho = None
        self.link_to_ac = (body[17] & 0x01) > 0
        self.sleep_mode = (body[17] & 0x02) > 0
        self.eco_mode = (body[17] & 0x04) > 0
        if (body[19] & 0x02) > 0:
            self.aux_heating = (body[17] & 0x08) > 0
        else:
            self.aux_heating = None
        self.powerful_purify = (body[17] & 0x10) > 0
        self.filter_cleaning_reminder = (body[18] & 0x01) > 0
        self.filter_change_reminder = (body[18] & 0x02) > 0
        self.error_code = body[24]


class CENotifyMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.pm25 = (body[1] << 8) + body[2]
        self.co2 = (body[3] << 8) + body[4]
        if body[5] != 0xFF:
            self.current_humidity = (body[5] << 8) + body[6] / 10
        else:
            self.current_humidity = None
        if body[7] != 0xFF:
            self.current_temperature = (body[7] << 8) + (body[8] - 60) / 2
        else:
            self.current_temperature = None
        if body[9] != 0xFF:
            self.hcho = (body[9] << 8) + body[10] / 1000
        else:
            self.hcho = None
        self.error_code = body[12]


class MessageCEResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if (
            self.message_type in [MessageType.query, MessageType.set]
            and self.body_type == 0x01
        ) or (self.message_type == MessageType.notify1 and self.body_type == 0x02):
            self.set_body(CEGeneralMessageBody(super().body))
        elif self.message_type == MessageType.notify1 and self.body_type == 0x01:
            self.set_body(CENotifyMessageBody(super().body))
        self.set_attr()
