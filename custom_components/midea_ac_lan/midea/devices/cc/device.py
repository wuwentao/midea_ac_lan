import logging
from .message import (
    MessageQuery,
    MessageSet,
    MessageCCResponse
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    mode = "mode"
    target_temperature = "target_temperature"
    fan_speed = "fan_speed"
    eco_mode = "eco_mode"
    sleep_mode = "sleep_mode"
    night_light = "night_light"
    aux_heating = "aux_heating"
    swing = "swing"
    ventilation = "ventilation"
    temperature_precision = "temperature_precision"
    fan_speed_level = "fan_speed_level"
    indoor_temperature = "indoor_temperature"
    aux_heat_status = "aux_heat_status"
    auto_aux_heat_running = "auto_aux_heat_running"
    temp_fahrenheit = "temp_fahrenheit"


class MideaCCDevice(MideaDevice):
    _fan_speeds_7level = {
        0x01: "Level 1", 0x02: "Level 2", 0x04: "Level 3",
        0x08: "Level 4", 0x10: "Level 5", 0x20: "Level 6",
        0x40: "Level 7", 0x80: "Auto",
    }
    _fan_speeds_3level = {
        0x01: "Low", 0x08: "Medium", 0x40: "High", 0x80: "Auto"
    }

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
            device_type=0xCC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.mode: 1,
                DeviceAttributes.target_temperature: 26.0,
                DeviceAttributes.fan_speed: 0x80,
                DeviceAttributes.sleep_mode: False,
                DeviceAttributes.eco_mode: False,
                DeviceAttributes.night_light: False,
                DeviceAttributes.ventilation: False,
                DeviceAttributes.aux_heating: False,
                DeviceAttributes.aux_heat_status: 0,
                DeviceAttributes.auto_aux_heat_running: False,
                DeviceAttributes.swing: False,
                DeviceAttributes.fan_speed_level: None,
                DeviceAttributes.indoor_temperature: None,
                DeviceAttributes.temperature_precision: 1,
                DeviceAttributes.temp_fahrenheit: False
            })
        self._fan_speeds = None

    @property
    def fan_modes(self):
        return None if self._fan_speeds is None else list(self._fan_speeds.values())

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageCCResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        fan_speed = None
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.fan_speed:
                    fan_speed = value
                else:
                    self._attributes[status] = getattr(message, str(status))
                    new_status[str(status)] = getattr(message, str(status))
        if fan_speed is not None and self._attributes[DeviceAttributes.fan_speed_level] is not None:
            if self._fan_speeds is None:
                if self._attributes[DeviceAttributes.fan_speed_level]:
                    self._fan_speeds = MideaCCDevice._fan_speeds_3level
                else:
                    self._fan_speeds = MideaCCDevice._fan_speeds_7level
            if fan_speed in self._fan_speeds.keys():
                self._attributes[DeviceAttributes.fan_speed] = self._fan_speeds.get(fan_speed)
            else:
                self._attributes[DeviceAttributes.fan_speed] = None
            new_status[DeviceAttributes.fan_speed.value] = self._attributes[DeviceAttributes.fan_speed]
        aux_heating = \
            self._attributes[DeviceAttributes.aux_heat_status] == 1 or \
            self._attributes[DeviceAttributes.auto_aux_heat_running]
        if self._attributes[DeviceAttributes.aux_heating] != aux_heating:
            self._attributes[DeviceAttributes.aux_heating] = aux_heating
            new_status[DeviceAttributes.aux_heating.value] = self._attributes[DeviceAttributes.aux_heating]
        return new_status

    def make_message_set(self):
        message = MessageSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.mode = self._attributes[DeviceAttributes.mode]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.fan_speed = list(self._fan_speeds.keys())[
            list(self._fan_speeds.values()).index(self._attributes[DeviceAttributes.fan_speed])
        ]
        message.eco_mode = self._attributes[DeviceAttributes.eco_mode]
        message.sleep_mode = self._attributes[DeviceAttributes.sleep_mode]
        message.night_light = self._attributes[DeviceAttributes.night_light]
        message.aux_heat_status = self._attributes[DeviceAttributes.aux_heat_status]
        message.swing = self._attributes[DeviceAttributes.swing]
        return message

    def set_target_temperature(self, target_temperature, mode):
        message = self.make_message_set()
        message.target_temperature = target_temperature
        if mode is not None:
            message.power = True
            message.mode = mode
        self.build_send(message)

    def set_attribute(self, attr, value):
        # if nat a sensor
        if attr not in [DeviceAttributes.indoor_temperature,
                        DeviceAttributes.temperature_precision,
                        DeviceAttributes.fan_speed_level,
                        DeviceAttributes.aux_heat_status,
                        DeviceAttributes.auto_aux_heat_running]:
            message = self.make_message_set()
            if attr == DeviceAttributes.fan_speed:
                if value in self._fan_speeds.values():
                    message.fan_speed = list(self._fan_speeds.keys())[
                        list(self._fan_speeds.values()).index(value)
                    ]
            else:
                setattr(message, str(attr), value)
                if attr == DeviceAttributes.mode:
                    setattr(message, str(DeviceAttributes.power.value), True)
                elif attr == DeviceAttributes.eco_mode and value:
                    setattr(message, str(DeviceAttributes.sleep_mode.value), False)
                elif attr == DeviceAttributes.sleep_mode and value:
                    setattr(message, str(DeviceAttributes.eco_mode.value), False)
                elif attr == DeviceAttributes.aux_heating:
                    if value:
                        setattr(message, DeviceAttributes.aux_heat_status, 1)
                    else:
                        setattr(message, DeviceAttributes.aux_heat_status, 2)
            self.build_send(message)


class MideaAppliance(MideaCCDevice):
    pass
