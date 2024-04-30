import logging
from .message import (
    MessageQuery,
    MessageA1Response,
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
    prompt_tone = "prompt_tone"
    child_lock = "child_lock"
    mode = "mode"
    fan_speed = "fan_speed"
    swing = "swing"
    target_humidity = "target_humidity"
    anion = "anion"
    tank = "tank"
    water_level_set = "water_level_set"
    tank_full = "tank_full"
    current_humidity = "current_humidity"
    current_temperature = "current_temperature"


class MideaA1Device(MideaDevice):
    _modes = [
        "Manual", "Continuous", "Auto", "Clothes-Dry", "Shoes-Dry"
    ]
    _speeds = {
        1: "Lowest", 40: "Low", 60: "Medium", 80: "High", 102: "Auto", 127: "Off"
    }
    _water_level_sets = [
        "25", "50", "75", "100"
    ]

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
            device_type=0xA1,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.prompt_tone: True,
                DeviceAttributes.child_lock: False,
                DeviceAttributes.mode: None,
                DeviceAttributes.fan_speed: 60,
                DeviceAttributes.swing: False,
                DeviceAttributes.target_humidity: 35,
                DeviceAttributes.anion: False,
                DeviceAttributes.tank: 0,
                DeviceAttributes.water_level_set: 50,
                DeviceAttributes.tank_full: None,
                DeviceAttributes.current_humidity: None,
                DeviceAttributes.current_temperature: None
            })

    @property
    def modes(self):
        return MideaA1Device._modes

    @property
    def fan_speeds(self):
        return list(MideaA1Device._speeds.values())

    @property
    def water_level_sets(self):
        return MideaA1Device._water_level_sets

    def build_query(self):
        return [
            MessageQuery(self._protocol_version)
        ]

    def process_message(self, msg):
        message = MessageA1Response(msg)
        self._protocol_version = message.protocol_version
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.mode:
                    if value <= len(MideaA1Device._modes):
                        self._attributes[status] = MideaA1Device._modes[value - 1]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.fan_speed:
                    if value in MideaA1Device._speeds.keys():
                        self._attributes[status] = MideaA1Device._speeds.get(value)
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.water_level_set:
                    self._attributes[status] = str(value)
                else:
                    self._attributes[status] = value
                tank_full = (self._attributes[DeviceAttributes.tank] >=
                             int(self._attributes[DeviceAttributes.water_level_set]))
                if self._attributes[DeviceAttributes.tank_full] is None or self._attributes[DeviceAttributes.tank_full] != tank_full:
                    self._attributes[DeviceAttributes.tank_full] = tank_full
                    new_status[str(DeviceAttributes.tank_full)] = tank_full
                new_status[str(status)] = self._attributes[status]
        return new_status

    def make_message_set(self):
        message = MessageSet(self._protocol_version)
        message.power = self._attributes[DeviceAttributes.power]
        message.prompt_tone = self._attributes[DeviceAttributes.prompt_tone]
        message.child_lock = self._attributes[DeviceAttributes.child_lock]
        if self._attributes[DeviceAttributes.mode] in MideaA1Device._modes:
            message.mode = MideaA1Device._modes.index(self._attributes[DeviceAttributes.mode]) + 1
        else:
            message.mode = 1
        message.fan_speed = 40 if self._attributes[DeviceAttributes.fan_speed] is None else \
            list(MideaA1Device._speeds.keys())[list(MideaA1Device._speeds.values()).index(
                self._attributes[DeviceAttributes.fan_speed]
            )]
        message.target_humidity = self._attributes[DeviceAttributes.target_humidity]
        message.swing = self._attributes[DeviceAttributes.swing]
        message.anion = self._attributes[DeviceAttributes.anion]
        message.water_level_set = int(self._attributes[DeviceAttributes.water_level_set])
        return message

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.prompt_tone:
            self._attributes[DeviceAttributes.prompt_tone] = value
            self.update_all({DeviceAttributes.prompt_tone.value: value})
        else:
            message = self.make_message_set()
            if attr == DeviceAttributes.mode:
                if value in MideaA1Device._modes:
                    message.mode = MideaA1Device._modes.index(value) + 1
            elif attr == DeviceAttributes.fan_speed:
                if value in MideaA1Device._speeds.values():
                    message.fan_speed = list(MideaA1Device._speeds.keys())[
                        list(MideaA1Device._speeds.values()).index(value)
                    ]
            elif attr == DeviceAttributes.water_level_set:
                if value in MideaA1Device._water_level_sets:
                    message.water_level_set = int(value)
            else:
                setattr(message, str(attr), value)
            self.build_send(message)


class MideaAppliance(MideaA1Device):
    pass
