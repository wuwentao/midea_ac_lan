import logging
import json
from .message import (
    MessageQuery,
    MessageFCResponse,
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
    mode = "mode"
    fan_speed = "fan_speed"
    anion = "anion"
    screen_display = "screen_display"
    detect_mode = "detect_mode"
    pm25 = "pm25"
    tvoc = "tvoc"
    hcho = "hcho"
    child_lock = "child_lock"
    prompt_tone = "prompt_tone"
    filter1_life = "filter1_life"
    filter2_life = "filter2_life"
    standby = "standby"


class MideaFCDevice(MideaDevice):
    _modes = {
        0x00: "Standby", 0x10: "Auto", 0x20: "Manual", 0x30: "Sleep", 0x40: "Fast", 0x50: "Smoke"
    }
    _speeds = {
        1: "Auto", 4: "Standby", 39: "Low", 59: "Medium", 80: "High"
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
            device_type=0xFC,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.mode: None,
                DeviceAttributes.fan_speed: None,
                DeviceAttributes.anion: False,
                DeviceAttributes.standby: False,
                DeviceAttributes.screen_display: None,
                DeviceAttributes.detect_mode: None,
                DeviceAttributes.pm25: None,
                DeviceAttributes.tvoc: None,
                DeviceAttributes.hcho: None,
                DeviceAttributes.child_lock: False,
                DeviceAttributes.prompt_tone: True,
                DeviceAttributes.filter1_life: None,
                DeviceAttributes.filter2_life: None,
            })

        self._standby_detect_default = [40, 20]
        self._standby_detect = self._standby_detect_default
        self.set_customize(customize)

    @property
    def modes(self):
        return list(MideaFCDevice._modes.values())

    @property
    def fan_speeds(self):
        return list(MideaFCDevice._speeds.values())

    @property
    def screen_displays(self):
        return list(MideaFCDevice._screen_displays.values())

    @property
    def detect_modes(self):
        return self._detect_modes

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageFCResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.mode:
                    if value in MideaFCDevice._modes.keys():
                        self._attributes[status] = MideaFCDevice._modes.get(value)
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.fan_speed:
                    if value in MideaFCDevice._speeds.keys():
                        self._attributes[status] = MideaFCDevice._speeds.get(value)
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.screen_display:
                    if value in MideaFCDevice._screen_displays.keys():
                        self._attributes[status] = MideaFCDevice._screen_displays.get(value)
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.detect_mode:
                    if value < len(MideaFCDevice._detect_modes):
                        self._attributes[status] = MideaFCDevice._detect_modes[value]
                    else:
                        self._attributes[status] = None
                else:

                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def make_message_set(self):
        message = MessageSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.child_lock = self._attributes[DeviceAttributes.child_lock]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.anion = self._attributes[DeviceAttributes.anion]
        message.standby = self._attributes[DeviceAttributes.standby]
        message.screen_display = self._attributes[DeviceAttributes.screen_display]
        message.detect_mode = 0 if self._attributes[DeviceAttributes.detect_mode] is None else \
            MideaFCDevice._detect_modes.index(self._attributes[DeviceAttributes.detect_mode])
        message.mode = 0x10 if self._attributes[DeviceAttributes.mode] is None else \
            list(MideaFCDevice._modes.keys())[list(MideaFCDevice._modes.values()).index(
                self._attributes[DeviceAttributes.mode]
            )]
        message.fan_speed = 39 if self._attributes[DeviceAttributes.fan_speed] is None else \
            list(MideaFCDevice._speeds.keys())[list(MideaFCDevice._speeds.values()).index(
                self._attributes[DeviceAttributes.fan_speed]
            )]
        message.screen_display = 0 if self._attributes[DeviceAttributes.screen_display] is None else \
            list(MideaFCDevice._screen_displays.keys())[list(MideaFCDevice._screen_displays.values()).index(
                self._attributes[DeviceAttributes.screen_display]
            )]
        message.standby_detect = self._standby_detect
        return message

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.prompt_tone:
            self._attributes[DeviceAttributes.prompt_tone] = value
            self.update_all({DeviceAttributes.prompt_tone.value: value})
        else:
            message = self.make_message_set()
            if attr == DeviceAttributes.mode:
                if value in MideaFCDevice._modes.values():
                    message.mode = list(MideaFCDevice._modes.keys())[
                        list(MideaFCDevice._modes.values()).index(value)
                    ]
            elif attr == DeviceAttributes.fan_speed:
                if value in MideaFCDevice._speeds.values():
                    message.fan_speed = list(MideaFCDevice._speeds.keys())[
                        list(MideaFCDevice._speeds.values()).index(value)
                    ]
            elif attr == DeviceAttributes.screen_display:
                if value in MideaFCDevice._screen_displays.values():
                    message.screen_display = list(MideaFCDevice._screen_displays.keys())[
                        list(MideaFCDevice._screen_displays.values()).index(value)
                    ]
                elif not value:
                    message.screen_display = 7
            elif attr == DeviceAttributes.detect_mode:
                if value in MideaFCDevice._detect_modes:
                    message.detect_mode = MideaFCDevice._detect_modes.index(value)
                elif not value:
                    message.detect_mode = 0
            else:
                setattr(message, str(attr), value)
            self.build_send(message)

    def set_customize(self, customize):
        self._standby_detect = self._standby_detect_default
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "standby_detect" in params:
                    settings = params.get("standby_detect")
                    if len(settings) == 2 and settings[0] > settings[1]:
                        self._standby_detect = settings
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"standby_detect": self._standby_detect})


class MideaAppliance(MideaFCDevice):
    pass
