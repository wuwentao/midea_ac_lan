from ...core.message import MessageBody, MessageRequest, MessageResponse, MessageType


class MessageC3Base(MessageRequest):
    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xC3,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type,
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageC3Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x01,
        )

    @property
    def _body(self):
        return bytearray([])


class MessageSet(MessageC3Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x01,
        )
        self.zone1_power = False
        self.zone2_power = False
        self.dhw_power = False
        self.mode = 0
        self.zone_target_temp = [25, 25]
        self.dhw_target_temp = 40
        self.room_target_temp = 25
        self.zone1_curve = False
        self.zone2_curve = False
        self.disinfect = False
        self.fast_dhw = False
        self.tbh = False

    @property
    def _body(self):
        # Byte 1
        zone1_power = 0x01 if self.zone1_power else 0x00
        zone2_power = 0x02 if self.zone2_power else 0x00
        dhw_power = 0x04 if self.dhw_power else 0x00
        # Byte 7
        zone1_curve = 0x01 if self.zone1_curve else 0x00
        zone2_curve = 0x02 if self.zone2_curve else 0x00
        disinfect = 0x04 if self.disinfect or self.tbh else 0x00
        fast_dhw = 0x08 if self.fast_dhw else 0x00
        room_target_temp = int(self.room_target_temp * 2)
        zone1_target_temp = int(self.zone_target_temp[0])
        zone2_target_temp = int(self.zone_target_temp[1])
        dhw_target_temp = int(self.dhw_target_temp)
        return bytearray(
            [
                zone1_power | zone2_power | dhw_power,
                self.mode,
                zone1_target_temp,
                zone2_target_temp,
                dhw_target_temp,
                room_target_temp,
                zone1_curve | zone2_curve | disinfect | fast_dhw,
            ]
        )


class MessageSetSilent(MessageC3Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x05,
        )
        self.silent_mode = False
        self.super_silent = False

    @property
    def _body(self):
        silent_mode = 0x01 if self.silent_mode else 0
        super_silent = 0x02 if self.super_silent else 0

        return bytearray(
            [silent_mode | super_silent, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )


class MessageSetECO(MessageC3Base):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x07,
        )
        self.eco_mode = False

    @property
    def _body(self):
        eco_mode = 0x01 if self.eco_mode else 0

        return bytearray([eco_mode, 0x00, 0x00, 0x00, 0x00, 0x00])


class C3MessageBody(MessageBody):
    def __init__(self, body, data_offset=0):
        super().__init__(body)
        self.zone1_power = body[data_offset + 0] & 0x01 > 0
        self.zone2_power = body[data_offset + 0] & 0x02 > 0
        self.dhw_power = body[data_offset + 0] & 0x04 > 0
        self.zone1_curve = body[data_offset + 0] & 0x08 > 0
        self.zone2_curve = body[data_offset + 0] & 0x10 > 0
        self.disinfect = body[data_offset + 0] & 0x20 > 0
        self.tbh = body[data_offset + 0] & 0x20 > 0
        self.fast_dhw = body[data_offset + 0] & 0x40 > 0
        self.zone_temp_type = [
            body[data_offset + 1] & 0x10 > 0,
            body[data_offset + 1] & 0x20 > 0,
        ]
        self.silent_mode = body[data_offset + 2] & 0x02 > 0
        self.eco_mode = body[data_offset + 2] & 0x08 > 0
        self.mode = body[data_offset + 3]
        self.mode_auto = body[data_offset + 4]
        self.zone_target_temp = [body[data_offset + 5], body[data_offset + 6]]
        self.dhw_target_temp = body[data_offset + 7]
        self.room_target_temp = body[data_offset + 8] / 2
        self.zone_heating_temp_max = [body[data_offset + 9], body[data_offset + 13]]
        self.zone_heating_temp_min = [body[data_offset + 10], body[data_offset + 14]]
        self.zone_cooling_temp_max = [body[data_offset + 11], body[data_offset + 15]]
        self.zone_cooling_temp_min = [body[data_offset + 12], body[data_offset + 16]]
        self.room_temp_max = body[data_offset + 17] / 2
        self.room_temp_min = body[data_offset + 18] / 2
        self.dhw_temp_max = body[data_offset + 19]
        self.dhw_temp_min = body[data_offset + 20]
        self.tank_actual_temperature = body[data_offset + 21]
        self.error_code = body[data_offset + 22]


class C3Notify1MessageBody(MessageBody):
    def __init__(self, body, data_offset=0):
        super().__init__(body)
        status_byte = body[data_offset]
        self.status_tbh = (status_byte & 0x08) > 0
        self.status_dhw = (status_byte & 0x04) > 0
        self.status_ibh = (status_byte & 0x02) > 0
        self.status_heating = (status_byte & 0x01) > 0

        self.total_energy_consumption = (
            (body[data_offset + 1] << 32)
            + (body[data_offset + 2] << 16)
            + (body[data_offset + 3] << 8)
            + (body[data_offset + 4])
        )

        self.total_produced_energy = (
            (body[data_offset + 5] << 32)
            + (body[data_offset + 6] << 16)
            + (body[data_offset + 7] << 8)
            + (body[data_offset + 8])
        )
        base_value = body[data_offset + 9]
        self.outdoor_temperature = (base_value - 256) if base_value > 127 else base_value


class MessageC3Response(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        if (
            self.message_type
            in [MessageType.set, MessageType.notify1, MessageType.query]
            and self.body_type == 0x01
        ) or self.message_type == MessageType.notify2:
            self.set_body(C3MessageBody(super().body, data_offset=1))
        elif self.message_type == MessageType.notify1 and self.body_type == 0x04:
            self.set_body(C3Notify1MessageBody(super().body, data_offset=1))
        self.set_attr()
