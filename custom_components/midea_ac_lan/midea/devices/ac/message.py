from enum import IntEnum
from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody,
    NewProtocolMessageBody
)
from ...core.crc8 import calculate

BB_AC_MODES = [0, 3, 1, 2, 4, 5]


class NewProtocolTags(IntEnum):
    indoor_humidity = 0x0015
    screen_display = 0x0017
    breezeless = 0x0018
    prompt_tone = 0x001A
    indirect_wind = 0x0042
    fresh_air_1 = 0x0233
    fresh_air_2 = 0x004b


class MessageACBase(MessageRequest):
    _message_serial = 0

    def __init__(self, protocol_version, message_type, body_type):
        super().__init__(
            device_type=0xAC,
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=body_type
        )
        MessageACBase._message_serial += 1
        if MessageACBase._message_serial >= 254:
            MessageACBase._message_serial = 1
        self._message_id = MessageACBase._message_serial

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body + bytearray([self._message_id])
        body.append(calculate(body))
        return body


class MessageQuery(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x81, 0x00, 0xFF, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00,
        ])


class MessagePowerQuery(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x41)

    @property
    def _body(self):
        return bytearray([
            0x21, 0x01, 0x44, 0x00, 0x01
        ])

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body
        body.append(calculate(body))
        return body


class MessageToggleDisplay(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0x41)
        self.prompt_tone = False

    @property
    def _body(self):
        prompt_tone = 0x40 if self.prompt_tone else 0
        return bytearray([
            0x02 | prompt_tone,
            0x00, 0xFF, 0x02,
            0x00, 0x02, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00
        ])


class MessageNewProtocolQuery(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            body_type=0xB1)

    @property
    def _body(self):
        query_params = [
            NewProtocolTags.indirect_wind,
            NewProtocolTags.breezeless,
            NewProtocolTags.indoor_humidity,
            NewProtocolTags.screen_display,
            NewProtocolTags.fresh_air_1,
            NewProtocolTags.fresh_air_2
        ]

        _body = bytearray([len(query_params)])
        for param in query_params:
            _body.extend([param & 0xFF, param >> 8])
        return _body


class MessageSubProtocol(MessageACBase):
    def __init__(self, protocol_version, message_type, subprotocol_query_type):
        super().__init__(
            protocol_version=protocol_version,
            message_type=message_type,
            body_type=0xAA)
        self._subprotocol_query_type = subprotocol_query_type

    @property
    def _subprotocol_body(self):
        return bytes([])

    @property
    def body(self):
        body = bytearray([self.body_type]) + self._body
        body.append(calculate(body))
        body.append(self.checksum(body))
        return body

    @property
    def _body(self):
        _subprotocol_body = self._subprotocol_body
        _body = bytearray([
            6 + 2 + (len(_subprotocol_body) if _subprotocol_body is not None else 0),
            0x00, 0xFF, 0xFF, self._subprotocol_query_type
        ])
        if _subprotocol_body is not None:
            _body.extend(_subprotocol_body)
        return _body


class MessageSubProtocolQuery(MessageSubProtocol):
    def __init__(self, protocol_version, subprotocol_query_type):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.query,
            subprotocol_query_type=subprotocol_query_type)


class MessageSubProtocolSet(MessageSubProtocol):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            subprotocol_query_type=0x20)
        self.power = False
        self.mode = 0
        self.target_temperature = 20.0
        self.fan_speed = 102
        self.boost_mode = False
        self.aux_heating = False
        self.dry = False
        self.eco_mode = False
        self.sleep_mode = False
        self.sn8_flag = False
        self.timer = False
        self.prompt_tone = False

    @property
    def _subprotocol_body(self):
        power = 0x01 if self.power else 0
        dry = 0x10 if self.power and self.dry else 0
        boost_mode = 0x20 if self.boost_mode else 0
        aux_heating = 0x40 if self.aux_heating else 0x80
        sleep_mode = 0x80 if self.sleep_mode else 0
        try:
            mode = 0 if self.mode == 0 else BB_AC_MODES[self.mode] - 1
        except IndexError:
            mode = 2  # set Auto if invalid mode
        target_temperature = int(self.target_temperature * 2 + 30)
        water_model_temperature_set = int((self.target_temperature - 1) * 2 + 50)
        fan_speed = self.fan_speed
        eco = 0x40 if self.eco_mode else 0

        prompt_tone = 0x01 if self.prompt_tone else 0
        timer = 0x04 if (self.sn8_flag and self.timer) else 0
        return bytearray([
            0x02 | boost_mode | power | dry,  aux_heating, sleep_mode, 0x00,
            0x00, mode, target_temperature, fan_speed,
            0x32, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x01,
            0x01, 0x00, 0x01, water_model_temperature_set,
            prompt_tone, target_temperature, 0x32, 0x66,
            0x00, eco | timer, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00,
            0x08
        ])


class MessageGeneralSet(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0x40)
        self.power = False
        self.prompt_tone = True
        self.mode = 0
        self.target_temperature = 20.0
        self.fan_speed = 102
        self.swing_vertical = False
        self.swing_horizontal = False
        self.boost_mode = False
        self.smart_eye = False
        self.dry = False
        self.aux_heating = False
        self.eco_mode = False
        self.temp_fahrenheit = False
        self.sleep_mode = False
        self.natural_wind = False
        self.frost_protect = False
        self.comfort_mode = False

    @property
    def _body(self):
        # Byte1, Power, prompt_tone
        power = 0x01 if self.power else 0
        prompt_tone = 0x40 if self.prompt_tone else 0
        # Byte2, mode target_temperature
        mode = (self.mode << 5) & 0xe0
        target_temperature = (int(self.target_temperature) & 0xf) | \
                             (0x10 if int(round(self.target_temperature * 2)) % 2 != 0 else 0)
        # Byte 3, fan_speed
        fan_speed = self.fan_speed & 0x7f
        # Byte 7, swing_mode
        swing_mode = 0x30 | (0x0c if self.swing_vertical else 0) \
            | (0x03 if self.swing_horizontal else 0)
        # Byte 8, turbo
        boost_mode = 0x20 if self.boost_mode else 0
        # Byte 9 aux_heating eco_mode
        smart_eye = 0x01 if self.smart_eye else 0
        dry = 0x04 if self.dry else 0
        aux_heating = 0x08 if self.aux_heating else 0
        eco_mode = 0x80 if self.eco_mode else 0
        # Byte 10 temp_fahrenheit
        temp_fahrenheit = 0x04 if self.temp_fahrenheit else 0
        sleep_mode = 0x01 if self.sleep_mode else 0
        boost_mode_1 = 0x02 if self.boost_mode else 0
        # Byte 17 natural_wind
        natural_wind = 0x40 if self.natural_wind else 0
        # Byte 21 frost_protect
        frost_protect = 0x80 if self.frost_protect else 0
        # Byte 22 comfort_mode
        comfort_mode = 0x01 if self.comfort_mode else 0

        return bytearray([
            power | prompt_tone,
            mode | target_temperature,
            fan_speed,
            0x00, 0x00, 0x00,
            swing_mode,
            boost_mode,
            smart_eye | dry | aux_heating | eco_mode,
            temp_fahrenheit | sleep_mode | boost_mode_1,
            0x00, 0x00, 0x00, 0x00,
            0x00, 0x00,
            natural_wind,
            0x00, 0x00, 0x00,
            frost_protect,
            comfort_mode
        ])


class MessageNewProtocolSet(MessageACBase):
    def __init__(self, protocol_version):
        super().__init__(
            protocol_version=protocol_version,
            message_type=MessageType.set,
            body_type=0xB0)
        self.indirect_wind = None
        self.prompt_tone = None
        self.breezeless = None
        self.screen_display_alternate = None
        self.fresh_air_1 = None
        self.fresh_air_2 = None

    @property
    def _body(self):
        pack_count = 0
        payload = bytearray([0x00])
        if self.breezeless is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.breezeless,
                    value=bytearray([0x01 if self.breezeless else 0x00])
                ))
        if self.indirect_wind is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.indirect_wind,
                    value=bytearray([0x02 if self.indirect_wind else 0x01])
                ))
        if self.prompt_tone is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.prompt_tone,
                    value=bytearray([0x01 if self.prompt_tone else 0x00])
                ))
        if self.screen_display_alternate is not None:
            pack_count += 1
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.screen_display,
                    value=bytearray([0x64 if self.screen_display_alternate else 0x00])
                ))
        if self.fresh_air_1 is not None and len(self.fresh_air_1) == 2:
            pack_count += 1
            fresh_air_power = 2 if self.fresh_air_1[0] > 0 else 1
            fresh_air_fan_speed = self.fresh_air_1[1]
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.fresh_air_1,
                    value=bytearray([
                        fresh_air_power,
                        fresh_air_fan_speed,
                        0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0x00, 0x00
                    ])
                ))
        if self.fresh_air_2 is not None and len(self.fresh_air_2) == 2:
            pack_count += 1
            fresh_air_power = 1 if self.fresh_air_2[0] > 0 else 0
            fresh_air_fan_speed = self.fresh_air_2[1]
            payload.extend(
                NewProtocolMessageBody.pack(
                    param=NewProtocolTags.fresh_air_2,
                    value=bytearray([
                        fresh_air_power,
                        fresh_air_fan_speed,
                        0xFF
                    ])
                ))
        payload[0] = pack_count
        return payload


class XA0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.target_temperature = ((body[1] & 0x3E) >> 1) - 4 + 16.0 + (0.5 if body[1] & 0x40 > 0 else 0.0)
        self.mode = (body[2] & 0xe0) >> 5
        self.fan_speed = body[3] & 0x7f
        self.swing_vertical = (body[7] & 0xC) > 0
        self.swing_horizontal = (body[7] & 0x3) > 0
        self.boost_mode = ((body[8] & 0x20) > 0) or ((body[10] & 0x2) > 0)
        self.smart_eye = (body[9] & 0x01) > 0
        self.dry = (body[9] & 0x04) > 0
        self.aux_heating = (body[9] & 0x08) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.sleep_mode = (body[10] & 0x01) > 0
        self.natural_wind = (body[10] & 0x40) > 0
        self.full_dust = (body[13] & 0x20) > 0
        self.comfort_mode = (body[14] & 0x1) > 0 if len(body) > 16 else False


class XA1MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        if body[13] != 0xFF:
            temp_integer = int((body[13] - 50) / 2)
            temp_decimal = ((body[18] & 0xF) * 0.1) if len(body) > 20 else 0
            if body[13] > 49:
                self.indoor_temperature = temp_integer + temp_decimal
            else:
                self.indoor_temperature = temp_integer - temp_decimal
        if body[14] == 0xFF:
            self.outdoor_temperature = None
        else:
            temp_integer = int((body[14] - 50) / 2)
            temp_decimal = (((body[18] & 0xF0) >> 4) * 0.1) if len(body) > 20 else 0
            if body[14] > 49:
                self.outdoor_temperature = temp_integer + temp_decimal
            else:
                self.outdoor_temperature = temp_integer - temp_decimal
        self.indoor_humidity = body[17]


class XBXMessageBody(NewProtocolMessageBody):
    def __init__(self, body, bt):
        super().__init__(body, bt)
        params = self.parse()
        if NewProtocolTags.indirect_wind in params:
            self.indirect_wind = (params[NewProtocolTags.indirect_wind][0] == 0x02)
        if NewProtocolTags.indoor_humidity in params:
            self.indoor_humidity = params[NewProtocolTags.indoor_humidity][0]
        if NewProtocolTags.breezeless in params:
            self.breezeless = (params[NewProtocolTags.breezeless][0] == 1)
        if NewProtocolTags.screen_display in params:
            self.screen_display_alternate = (params[NewProtocolTags.screen_display][0] > 0)
            self.screen_display_new = True
        if NewProtocolTags.fresh_air_1 in params:
            self.fresh_air_1 = True
            data = params[NewProtocolTags.fresh_air_1]
            self.fresh_air_power = data[0] == 0x02
            self.fresh_air_fan_speed = data[1]
        if NewProtocolTags.fresh_air_2 in params:
            self.fresh_air_2 = True
            data = params[NewProtocolTags.fresh_air_2]
            self.fresh_air_power = data[0] > 0
            self.fresh_air_fan_speed = data[1]


class XC0MessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.power = (body[1] & 0x1) > 0
        self.mode = (body[2] & 0xe0) >> 5
        self.target_temperature = (body[2] & 0x0F) + 16.0 + (0.5 if body[0x02] & 0x10 > 0 else 0.0)
        self.fan_speed = body[3] & 0x7F
        self.swing_vertical = (body[7] & 0x0C) > 0
        self.swing_horizontal = (body[7] & 0x03) > 0
        self.boost_mode = ((body[8] & 0x20) > 0) or ((body[10] & 0x2) > 0)
        self.smart_eye = (body[8] & 0x40) > 0
        self.natural_wind = (body[9] & 0x2) > 0
        self.dry = (body[9] & 0x4) > 0
        self.eco_mode = (body[9] & 0x10) > 0
        self.aux_heating = (body[9] & 0x08) > 0
        self.temp_fahrenheit = (body[10] & 0x04) > 0
        self.sleep_mode = (body[10] & 0x01) > 0
        if body[11] != 0xFF:
            temp_integer = int((body[11] - 50) / 2)
            temp_decimal = (body[15] & 0x0F) * 0.1
            if body[11] > 49:
                self.indoor_temperature = temp_integer + temp_decimal
            else:
                self.indoor_temperature = temp_integer - temp_decimal
        if body[12] == 0xFF:
            self.outdoor_temperature = None
        else:
            temp_integer = int((body[12] - 50) / 2)
            temp_decimal = ((body[15] & 0xF0) >> 4) * 0.1
            if body[12] > 49:
                self.outdoor_temperature = temp_integer + temp_decimal
            else:
                self.outdoor_temperature = temp_integer - temp_decimal
        self.full_dust = (body[13] & 0x20) > 0
        self.screen_display = ((body[14] >> 4 & 0x7) != 0x07) and self.power
        self.frost_protect = (body[21] & 0x80) > 0 if len(body) >= 22 else False
        self.comfort_mode = (body[22] & 0x1) > 0 if len(body) >= 23 else False


class XC1MessageBody(MessageBody):
    def __init__(self, body, analysis_method=3):
        super().__init__(body)
        if body[3] == 0x44:
            self.total_energy_consumption = XC1MessageBody.parse_consumption(
                analysis_method,
                body[4], body[5], body[6], body[7]
            )
            self.current_energy_consumption = XC1MessageBody.parse_consumption(
                analysis_method,
                body[12], body[13], body[14], body[15]
            )
            self.realtime_power = XC1MessageBody.parse_power(
                analysis_method,
                body[16], body[17], body[18]
            )
        elif body[3] == 0x40:
            pass

    @staticmethod
    def parse_value(byte):
        return (byte >> 4) * 10 + (byte & 0x0F)

    @staticmethod
    def parse_power(analysis_method, byte1, byte2, byte3):
        if analysis_method == 1:
            return float(XC1MessageBody.parse_value(byte1) * 10000 +
                         XC1MessageBody.parse_value(byte2) * 100 +
                         XC1MessageBody.parse_value(byte3)) / 10
        elif analysis_method == 2:
            return float((byte1 << 16) + (byte2 << 8) + byte3) / 10
        else:
            return float(byte1 * 10000 + byte2 * 100 + byte3) / 10

    @staticmethod
    def parse_consumption(analysis_method, byte1, byte2, byte3, byte4):
        if analysis_method == 1:
            return float(XC1MessageBody.parse_value(byte1) * 1000000 +
                         XC1MessageBody.parse_value(byte2) * 10000 +
                         XC1MessageBody.parse_value(byte3) * 100 +
                         XC1MessageBody.parse_value(byte4)) / 100
        elif analysis_method == 2:
            return float((byte1 << 32) + (byte2 << 16) + (byte3 << 8) + byte4) / 10
        else:
            return float(byte1 * 1000000 + byte2 * 10000 + byte3 * 100 + byte4) / 100


class XBBMessageBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        subprotocol_head = body[:6]
        subprotocol_body = body[6:]
        data_type = subprotocol_head[-1]
        subprotocol_body_len = len(subprotocol_body)
        if data_type == 0x20 or data_type == 0x11:
            self.power = (subprotocol_body[0] & 0x1) > 0
            self.dry = (subprotocol_body[0] & 0x10) > 0
            self.boost_mode = (subprotocol_body[0] & 0x20) > 0
            self.aux_heating = (subprotocol_body[1] & 0x40) > 0
            self.sleep_mode = (subprotocol_body[2] & 0x80) > 0
            try:
                self.mode = BB_AC_MODES.index(subprotocol_body[5] + 1)
            except ValueError:
                self.mode = 0
            self.target_temperature = (subprotocol_body[6] - 30) / 2
            self.fan_speed = subprotocol_body[7]
            self.timer = (subprotocol_body[25] & 0x04) > 0 if subprotocol_body_len > 27 else False
            self.eco_mode = (subprotocol_body[25] & 0x40) > 0 if subprotocol_body_len > 27 else False
        elif data_type == 0x10:
            if subprotocol_body[8] & 0x80 == 0x80:
                self.indoor_temperature = (0 - (~(subprotocol_body[7] + subprotocol_body[8] * 256) + 1) & 0xffff) / 100
            else:
                self.indoor_temperature = (subprotocol_body[7] + subprotocol_body[8] * 256) / 100
            self.indoor_humidity = subprotocol_body[30]
            self.sn8_flag = subprotocol_body[80] == 0x31
        elif data_type == 0x12:
            pass
        elif data_type == 0x30:
            if subprotocol_body[6] & 0x80 == 0x80:
                self.outdoor_temperature = (0 - (~(subprotocol_body[5] + subprotocol_body[6] * 256) + 1) & 0xffff) / 100
            else:
                self.outdoor_temperature = (subprotocol_body[5] + subprotocol_body[6] * 256) / 100
        elif data_type == 0x13 or data_type == 0x21:
            pass


class MessageACResponse(MessageResponse):
    def __init__(self, message, power_analysis_method=3):
        super().__init__(message)
        if self.message_type == MessageType.notify2 and self.body_type == 0xA0:
            self.set_body(XA0MessageBody(super().body))
        elif self.message_type == MessageType.notify1 and self.body_type == 0xA1:
            self.set_body(XA1MessageBody(super().body))
        elif self.message_type in [MessageType.query, MessageType.set, MessageType.notify2] and \
                self.body_type in [0xB0, 0xB1, 0xB5]:
            self.set_body(XBXMessageBody(super().body, self.body_type))
        elif self.message_type in [MessageType.query, MessageType.set] and self.body_type == 0xC0:
            self.set_body(XC0MessageBody(super().body))
        elif self.message_type == MessageType.query and self.body_type == 0xC1:
            self.set_body(XC1MessageBody(super().body, power_analysis_method))
        elif self.message_type in [MessageType.set, MessageType.query, MessageType.notify2] and \
                self.body_type == 0xBB and len(super().body) >= 21:
            self.used_subprotocol = True
            self.set_body(XBBMessageBody(super().body))
        self.set_attr()
