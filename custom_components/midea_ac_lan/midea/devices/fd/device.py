import logging
from .message import (
    MessageQuery,
    MessageFDResponse,
    MessageSet
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    fan_speed = "fan_speed"
    prompt_tone = "prompt_tone"
    target_humidity = "target_humidity"
    current_humidity = "current_humidity"
    current_temperature = "current_temperature"
    tank = "tank"
    mode = "mode"
    screen_display = "screen_display"
    disinfect = "disinfect"


class MideaFDDevice(MideaDevice):
    _modes = [
        "Manual", "Auto", "Continuous", "Living-Room", "Bed-Room", "Kitchen", "Sleep"
    ]
    _speeds_old = {
        1: "Lowest", 40: "Low", 60: "Medium", 80: "High", 102: "Auto", 127: "Off"
    }
    _speeds_new = {
        1: "Lowest", 39: "Low", 59: "Medium", 80: "High", 101: "Auto", 127: "Off"
    }
    _screen_displays = {
        0: "Bright", 6: "Dim", 7: "Off"
    }
    _detect_modes = ["Off", "PM 2.5", "Methanal"]

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
            device_type=0xFD,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.fan_speed: None,
                DeviceAttributes.prompt_tone: True,
                DeviceAttributes.target_humidity: 60,
                DeviceAttributes.current_humidity: None,
                DeviceAttributes.current_temperature: None,
                DeviceAttributes.tank: 0,
                DeviceAttributes.mode: None,
                DeviceAttributes.screen_display: None,
                DeviceAttributes.disinfect: None,
            })
        if self.subtype > 5:
            self._speeds = MideaFDDevice._speeds_new
        else:
            self._speeds = MideaFDDevice._speeds_old

    @property
    def modes(self):
        return list(MideaFDDevice._modes)

    @property
    def fan_speeds(self):
        return list(self._speeds.values())

    @property
    def screen_displays(self):
        return list(MideaFDDevice._screen_displays.values())

    @property
    def detect_modes(self):
        return self._detect_modes

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):

        message = MessageFDResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.mode:
                    if value <= len(MideaFDDevice._modes):
                        self._attributes[status] = MideaFDDevice._modes[value - 1]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.fan_speed:
                    if value in self._speeds.keys():
                        self._attributes[status] = self._speeds.get(value)
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.screen_display:
                    if value in MideaFDDevice._screen_displays.keys():
                        self._attributes[status] = MideaFDDevice._screen_displays.get(value)
                    else:
                        self._attributes[status] = None
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def make_message_set(self):
        message = MessageSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.screen_display = self._attributes[DeviceAttributes.screen_display]
        message.disinfect = self._attributes[DeviceAttributes.disinfect]
        if self._attributes[DeviceAttributes.mode] in MideaFDDevice._modes:
            message.mode = MideaFDDevice._modes.index(self._attributes[DeviceAttributes.mode]) + 1
        else:
            message.mode = 1
        message.fan_speed = 40 if self._attributes[DeviceAttributes.fan_speed] is None else \
            list(self._speeds.keys())[list(self._speeds.values()).index(
                self._attributes[DeviceAttributes.fan_speed]
            )]
        message.screen_display = 0 if self._attributes[DeviceAttributes.screen_display] is None else \
            list(MideaFDDevice._screen_displays.keys())[list(MideaFDDevice._screen_displays.values()).index(
                self._attributes[DeviceAttributes.screen_display]
            )]
        return message

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.prompt_tone:
            self._attributes[DeviceAttributes.prompt_tone] = value
            self.update_all({DeviceAttributes.prompt_tone.value: value})
        else:
            message = self.make_message_set()
            if attr == DeviceAttributes.mode:
                if value in MideaFDDevice._modes:
                    message.mode = MideaFDDevice._modes.index(value) + 1
            elif attr == DeviceAttributes.fan_speed:
                if value in self._speeds.values():
                    message.fan_speed = list(self._speeds.keys())[
                        list(self._speeds.values()).index(value)
                    ]
            elif attr == DeviceAttributes.screen_display:
                if value in MideaFDDevice._screen_displays.values():
                    message.screen_display = list(MideaFDDevice._screen_displays.keys())[
                        list(MideaFDDevice._screen_displays.values()).index(value)
                    ]
                elif not value:
                    message.screen_display = 7
            else:
                setattr(message, str(attr), value)
            self.build_send(message)


class MideaAppliance(MideaFDDevice):
    pass
