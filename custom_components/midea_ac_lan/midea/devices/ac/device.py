import logging
import json
from .message import (
    MessageQuery,
    MessageToggleDisplay,
    MessageNewProtocolQuery,
    MessageACResponse,
    MessageGeneralSet,
    MessageNewProtocolSet,
    MessagePowerQuery,
    MessageSubProtocolQuery,
    MessageSubProtocolSet
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    prompt_tone = "prompt_tone"
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"
    swing_vertical = "swing_vertical"
    swing_horizontal = "swing_horizontal"
    boost_mode = "boost_mode"
    smart_eye = "smart_eye"
    dry = "dry"
    eco_mode = "eco_mode"
    aux_heating = "aux_heating"
    sleep_mode = "sleep_mode"
    natural_wind = "natural_wind"
    temp_fahrenheit = "temp_fahrenheit"
    screen_display = "screen_display"
    screen_display_alternate = "screen_display_alternate"
    full_dust = "full_dust"
    frost_protect = "frost_protect"
    comfort_mode = "comfort_mode"
    indoor_temperature = "indoor_temperature"
    outdoor_temperature = "outdoor_temperature"
    indirect_wind = "indirect_wind"
    indoor_humidity = "indoor_humidity"
    breezeless = "breezeless"
    fresh_air_power = "fresh_air_power"
    fresh_air_fan_speed = "fresh_air_fan_speed"
    fresh_air_mode = "fresh_air_mode"
    fresh_air_1 = "fresh_air_1"
    fresh_air_2 = "fresh_air_2"
    total_energy_consumption = "total_energy_consumption"
    current_energy_consumption = "current_energy_consumption"
    realtime_power = "realtime_power"


class MideaACDevice(MideaDevice):
    _fresh_air_fan_speeds = {
        0: "Off", 20: "Silent", 40: "Low", 60: "Medium", 80: "High", 100: "Full"
    }
    _fresh_air_fan_speeds_rev = dict(reversed(_fresh_air_fan_speeds.items()))

    def __init__(
            self,
            name: str,
            device_id: int,
            ip_address: str,
            port: int,
            token: str,
            key: str,
            protocol: int,
            model: str,
            subtype: int,
            customize: str
    ):
        super().__init__(
            name=name,
            device_id=device_id,
            device_type=0xAC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.prompt_tone: True,
                DeviceAttributes.power: False,
                DeviceAttributes.mode: 0,
                DeviceAttributes.target_temperature: 24.0,
                DeviceAttributes.fan_speed: 102,
                DeviceAttributes.swing_vertical: False,
                DeviceAttributes.swing_horizontal: False,
                DeviceAttributes.smart_eye: False,
                DeviceAttributes.dry: False,
                DeviceAttributes.aux_heating: False,
                DeviceAttributes.boost_mode: False,
                DeviceAttributes.sleep_mode: False,
                DeviceAttributes.frost_protect: False,
                DeviceAttributes.comfort_mode: False,
                DeviceAttributes.eco_mode: False,
                DeviceAttributes.natural_wind: False,
                DeviceAttributes.temp_fahrenheit: False,
                DeviceAttributes.screen_display: False,
                DeviceAttributes.screen_display_alternate: False,
                DeviceAttributes.full_dust: False,
                DeviceAttributes.indoor_temperature: None,
                DeviceAttributes.outdoor_temperature: None,
                DeviceAttributes.indirect_wind: False,
                DeviceAttributes.indoor_humidity: None,
                DeviceAttributes.breezeless: False,
                DeviceAttributes.total_energy_consumption: None,
                DeviceAttributes.current_energy_consumption: None,
                DeviceAttributes.realtime_power: None,
                DeviceAttributes.fresh_air_power: False,
                DeviceAttributes.fresh_air_fan_speed: 0,
                DeviceAttributes.fresh_air_mode: None,
                DeviceAttributes.fresh_air_1: None,
                DeviceAttributes.fresh_air_2: None,
            })
        self._fresh_air_version = None
        self._default_temperature_step = 0.5
        self._temperature_step = None
        self._used_subprotocol = False
        self._bb_sn8_flag = False
        self._bb_timer = False
        self._power_analysis_method = None
        self._default_power_analysis_method = 1
        self.set_customize(customize)

    @property
    def temperature_step(self):
        return self._temperature_step

    @property
    def fresh_air_fan_speeds(self):
        return list(MideaACDevice._fresh_air_fan_speeds.values())

    def build_query(self):
        if self._used_subprotocol:
            return [
                MessageSubProtocolQuery(self._protocol_version, 0x10),
                MessageSubProtocolQuery(self._protocol_version, 0x11),
                MessageSubProtocolQuery(self._protocol_version, 0x30)
            ]
        return [
            MessageQuery(self._protocol_version),
            MessageNewProtocolQuery(self._protocol_version),
            MessagePowerQuery(self._protocol_version)
        ]

    def process_message(self, msg):
        message = MessageACResponse(msg, self._power_analysis_method)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        has_fresh_air = False
        if hasattr(message, "used_subprotocol"):
            self._used_subprotocol = True
            if hasattr(message, "sn8_flag"):
                self._bb_sn8_flag = message.sn8_flag
            if hasattr(message, "timer"):
                self._bb_timer = message.timer
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.fresh_air_power:
                    has_fresh_air = True
                self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        if has_fresh_air:
            if self._attributes[DeviceAttributes.fresh_air_power]:
                for k, v in MideaACDevice._fresh_air_fan_speeds_rev.items():
                    if self._attributes[DeviceAttributes.fresh_air_fan_speed] > k:
                        break
                    else:
                        self._attributes[DeviceAttributes.fresh_air_mode] = v
            else:
                self._attributes[DeviceAttributes.fresh_air_mode] = "Off"
            new_status[DeviceAttributes.fresh_air_mode.value] = self._attributes[DeviceAttributes.fresh_air_mode]
        if not self._attributes[DeviceAttributes.power] or \
                (DeviceAttributes.swing_vertical in new_status and self._attributes[DeviceAttributes.swing_vertical]):
            self._attributes[DeviceAttributes.indirect_wind] = False
            new_status[DeviceAttributes.indirect_wind.value] = False
        if not self._attributes[DeviceAttributes.power]:
            self._attributes[DeviceAttributes.screen_display] = False
            new_status[DeviceAttributes.screen_display.value] = False
        if self._attributes[DeviceAttributes.fresh_air_1] is not None:
            self._fresh_air_version = DeviceAttributes.fresh_air_1
        elif self._attributes[DeviceAttributes.fresh_air_2] is not None:
            self._fresh_air_version = DeviceAttributes.fresh_air_2
        return new_status

    def make_message_set(self):
        message = MessageGeneralSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
        message.swing_vertical = self._attributes[DeviceAttributes.swing_vertical]
        message.swing_horizontal = self._attributes[DeviceAttributes.swing_horizontal]
        message.boost_mode = self._attributes[DeviceAttributes.boost_mode]
        message.smart_eye = self._attributes[DeviceAttributes.smart_eye]
        message.dry = self._attributes[DeviceAttributes.dry]
        message.eco_mode = self._attributes[DeviceAttributes.eco_mode]
        message.aux_heating = self._attributes[DeviceAttributes.aux_heating]
        message.sleep_mode = self._attributes[DeviceAttributes.sleep_mode]
        message.natural_wind = self._attributes[DeviceAttributes.natural_wind]
        message.temp_fahrenheit = self._attributes[DeviceAttributes.temp_fahrenheit]
        message.frost_protect = self._attributes[DeviceAttributes.frost_protect]
        message.comfort_mode = self._attributes[DeviceAttributes.comfort_mode]
        return message

    def make_subptotocol_message_set(self):
        message = MessageSubProtocolSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.aux_heating = self._attributes[DeviceAttributes.aux_heating]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
        message.boost_mode = self._attributes[DeviceAttributes.boost_mode]
        message.dry = self._attributes[DeviceAttributes.dry]
        message.eco_mode = self._attributes[DeviceAttributes.eco_mode]
        message.sleep_mode = self._attributes[DeviceAttributes.sleep_mode]
        message.sn8_flag = self._bb_sn8_flag
        message.timer = self._bb_timer
        return message

    def make_message_uniq_set(self):
        if self._used_subprotocol:
            message = self.make_subptotocol_message_set()
        else:
            message = self.make_message_set()
        return message

    def set_attribute(self, attr, value):
        # if nat a sensor
        message = None
        if attr not in [DeviceAttributes.indoor_temperature,
                        DeviceAttributes.outdoor_temperature,
                        DeviceAttributes.indoor_humidity,
                        DeviceAttributes.full_dust,
                        DeviceAttributes.total_energy_consumption,
                        DeviceAttributes.current_energy_consumption,
                        DeviceAttributes.realtime_power]:
            if attr == DeviceAttributes.prompt_tone:
                self._attributes[DeviceAttributes.prompt_tone] = value
                self.update_all({DeviceAttributes.prompt_tone.value: value})
            elif attr == DeviceAttributes.screen_display:
                message = MessageToggleDisplay(self._protocol_version)
                message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
            elif attr in [
                    DeviceAttributes.indirect_wind,
                    DeviceAttributes.breezeless,
                    DeviceAttributes.screen_display_alternate
            ]:
                message = MessageNewProtocolSet(self._protocol_version)
                setattr(message, str(attr), value)
                message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
            elif attr == DeviceAttributes.fresh_air_power:
                if self._fresh_air_version is not None:
                    message = MessageNewProtocolSet(self._protocol_version)
                    setattr(
                        message,
                        str(self._fresh_air_version),
                        [value, self._attributes[DeviceAttributes.fresh_air_fan_speed]]
                    )
            elif attr == DeviceAttributes.fresh_air_mode:
                if value in MideaACDevice._fresh_air_fan_speeds.values():
                    speed = list(MideaACDevice._fresh_air_fan_speeds.keys())[
                        list(MideaACDevice._fresh_air_fan_speeds.values()).index(value)
                    ]
                    fresh_air = [True, speed] if speed > 0 else \
                        [False, self._attributes[DeviceAttributes.fresh_air_fan_speed]]
                    message = MessageNewProtocolSet(self._protocol_version)
                    setattr(
                        message,
                        str(self._fresh_air_version),
                        fresh_air
                    )
                elif not value:
                    message = MessageNewProtocolSet(self._protocol_version)
                    setattr(
                        message,
                        str(self._fresh_air_version),
                        [False, self._attributes[DeviceAttributes.fresh_air_fan_speed]]
                    )
            elif attr == DeviceAttributes.fresh_air_fan_speed:
                if self._fresh_air_version is not None:
                    message = MessageNewProtocolSet(self._protocol_version)
                    fresh_air = [True, value] if value > 0 else \
                        [False, self._attributes[DeviceAttributes.fresh_air_fan_speed]]
                    setattr(
                        message,
                        str(self._fresh_air_version),
                        fresh_air
                    )
            elif attr in self._attributes.keys():
                message = self.make_message_uniq_set()
                if attr in [
                    DeviceAttributes.boost_mode,
                    DeviceAttributes.sleep_mode,
                    DeviceAttributes.frost_protect,
                    DeviceAttributes.comfort_mode,
                    DeviceAttributes.eco_mode
                ]:
                    message.boost_mode = False
                    message.sleep_mode = False
                    message.comfort_mode = False
                    message.eco_mode = False
                    message.frost_protect = False
                setattr(message, str(attr), value)
                if attr == DeviceAttributes.mode:
                    setattr(message, str(DeviceAttributes.power.value), True)
        if message is not None:
            self.build_send(message)

    def set_target_temperature(self, target_temperature, mode):
        message = self.make_message_uniq_set()
        message.target_temperature = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    def set_swing(self, swing_vertical, swing_horizontal):
        message = self.make_message_uniq_set()
        message.swing_vertical = swing_vertical
        message.swing_horizontal = swing_horizontal
        self.build_send(message)

    def set_customize(self, customize):
        self._temperature_step = self._default_temperature_step
        self._power_analysis_method = self._default_power_analysis_method
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "temperature_step" in params:
                    self._temperature_step = params.get("temperature_step")
                if params and "power_analysis_method" in params:
                    self._power_analysis_method = params.get("power_analysis_method")
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"temperature_step": self._temperature_step})


class MideaAppliance(MideaACDevice):
    pass
