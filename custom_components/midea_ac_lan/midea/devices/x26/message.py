from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class Message26Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0x26,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(Message26Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01)

    @property
    def _body(self):
        return bytearray([
        ])


class MessageSet(Message26Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x01)
        self.fields = {}
        self.main_light = False
        self.night_light = False
        self.mode = 0
        self.direction = 0xFD

    def read_field(self, field):
        value = self.fields.get(field, 0)
        return value if value else 0

    @property
    def _body(self):
        return bytearray([
            1 if self.main_light else 0,
            self.read_field("MAIN_LIGHT_BRIGHTNESS"),
            1 if self.night_light else 0,
            self.read_field("NIGHT_LIGHT_BRIGHTNESS"),
            self.read_field("RADAR_INDUCTION_ENABLE"),
            self.read_field("RADAR_INDUCTION_CLOSING_TIME"),
            self.read_field("LIGHT_INTENSITY_THRESHOLD"),
            self.read_field("RADAR_SENSITIVITY"),
            1 if self.mode == 1 or self.mode == 2 else 0,
            0 if not (self.mode == 1 or self.mode == 2) else 55 if self.mode == 1 else 30,
            self.read_field("HEATING_SPEED"),
            self.direction,
            1 if self.mode == 3 else 0,
            self.read_field("BATH_HEATING_TIME"),
            self.read_field("BATH_TEMPERATURE"),
            self.read_field("BATH_SPEED"),
            self.direction,
            1 if self.mode == 5 else 0,
            self.read_field("VENTILATION_SPEED"),
            self.direction,
            1 if self.mode == 6 else 0,
            self.read_field("DRYING_TIME"),
            self.read_field("DRYING_TEMPERATURE"),
            self.read_field("DRYING_SPEED"),
            self.direction,
            1 if self.mode == 4 else 0,
            self.read_field("BLOWING_SPEED"),
            self.direction,
            self.read_field("DELAY_ENABLE"),
            self.read_field("DELAY_TIME"),
            self.read_field("SOFT_WIND_ENABLE"),
            self.read_field("SOFT_WIND_TIME"),
            self.read_field("SOFT_WIND_TEMPERATURE"),
            self.read_field("SOFT_WIND_SPEED"),
            self.read_field("SOFT_WIND_DIRECTION"),
            self.read_field("WINDLESS_ENABLE"),
            self.read_field("ANION_ENABLE"),
            self.read_field("SMELLY_ENABLE"),
            self.read_field("SMELLY_THRESHOLD")
        ])


class Message26Body(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.fields = {}
        self.main_light = self.read_byte(body, 1) > 0
        self.fields["MAIN_LIGHT_BRIGHTNESS"] = self.read_byte(body, 2)
        self.night_light = self.read_byte(body, 3) > 0
        self.fields["NIGHT_LIGHT_BRIGHTNESS"] = self.read_byte(body, 4)
        self.fields["RADAR_INDUCTION_ENABLE"] = self.read_byte(body, 5)
        self.fields["RADAR_INDUCTION_CLOSING_TIME"] = self.read_byte(body, 6)
        self.fields["LIGHT_INTENSITY_THRESHOLD"] = self.read_byte(body, 7)
        self.fields["RADAR_SENSITIVITY"] = self.read_byte(body, 8)
        heat_mode = self.read_byte(body, 9) > 0
        heat_temperature =  self.read_byte(body, 10)
        self.fields["HEATING_SPEED"] = self.read_byte(body, 11)
        heat_direction = self.read_byte(body, 12)
        bath_mode = self.read_byte(body, 13) > 0
        self.fields["BATH_HEATING_TIME"] = self.read_byte(body, 14)
        self.fields["BATH_TEMPERATURE"] = self.read_byte(body, 15)
        self.fields["BATH_SPEED"] = self.read_byte(body, 16)
        bath_direction = self.read_byte(body, 17)
        ventilation_mode = self.read_byte(body, 18) > 0
        self.fields["VENTILATION_SPEED"] = self.read_byte(body, 19)
        ventilation_direction = self.read_byte(body, 20)
        dry_mode = self.read_byte(body, 21) > 0
        self.fields["DRYING_TIME"] = self.read_byte(body, 22)
        self.fields["DRYING_TEMPERATURE"] = self.read_byte(body, 23)
        self.fields["DRYING_SPEED"] = self.read_byte(body, 24)
        dry_direction = self.read_byte(body, 25)
        blow_mode = self.read_byte(body, 26) > 0
        self.fields["BLOWING_SPEED"] = self.read_byte(body, 27)
        blow_direction = self.read_byte(body, 28)
        self.fields["DELAY_ENABLE"] = self.read_byte(body, 29)
        self.fields["DELAY_TIME"] = self.read_byte(body, 30)
        if self.read_byte(body, 31) != 0xFF:
            self.current_humidity = self.read_byte(body, 31)
        if self.read_byte(body, 32) != 0xFF:
            self.current_radar = self.read_byte(body, 32)
        if self.read_byte(body, 33) != 0xFF:
            self.current_temperature = self.read_byte(body, 33)
        self.fields["SOFT_WIND_ENABLE"] = self.read_byte(body, 38)
        self.fields["SOFT_WIND_TIME"] = self.read_byte(body, 39)
        self.fields["SOFT_WIND_TEMPERATURE"] = self.read_byte(body, 40)
        self.fields["SOFT_WIND_SPEED"] = self.read_byte(body, 41)
        self.fields["SOFT_WIND_DIRECTION"] = self.read_byte(body, 42)
        self.fields["WINDLESS_ENABLE"] = self.read_byte(body, 43)
        self.fields["ANION_ENABLE"] = self.read_byte(body, 44)
        self.fields["SMELLY_ENABLE"] = self.read_byte(body, 45)
        self.fields["SMELLY_THRESHOLD"] = self.read_byte(body, 46)
        self.mode = 0
        self.direction = 0xFD
        if heat_mode:
            if heat_temperature > 50:
                self.mode = 1
            else:
                self.mode = 2
            self.direction = heat_direction
        elif bath_mode:
            self.mode = 3
            self.direction = bath_direction
        elif blow_mode:
            self.mode = 4
            self.direction = blow_direction
        elif ventilation_mode:
            self.mode = 5
            self.direction = ventilation_direction
        elif dry_mode:
            self.mode = 6
            self.direction = dry_direction


class Message26Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if self.message_type in [MessageType.set, MessageType.notify1, MessageType.query] and self.body_type == 0x01:
            self.set_body(Message26Body(super().body))
        self.set_attr()

