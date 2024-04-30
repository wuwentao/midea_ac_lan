import logging
import json
from .message import (
    MessageQuery,
    MessageFAResponse,
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
    child_lock = "child_lock"
    mode = "mode"
    fan_speed = "fan_speed"
    oscillate = "oscillate"
    oscillation_angle = "oscillation_angle"
    tilting_angle = "tilting_angle"
    oscillation_mode = "oscillation_mode"


class MideaFADevice(MideaDevice):
    _oscillation_angles = [
        "Off", "30", "60", "90", "120", "180", "360"
    ]
    _tilting_angles = [
        "Off", "30", "60", "90", "120", "180", "360", "+60", "-60", "40"
    ]
    _oscillation_modes = [
        "Off", "Oscillation", "Tilting", "Curve-W", "Curve-8", "Reserved", "Both"
    ]
    _modes = [
        "Normal", "Natural", "Sleep", "Comfort", "Silent", "Baby",
        "Induction", "Circulation", "Strong", "Soft", "Customize", "Warm", "Smart"
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
            device_type=0xFA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.child_lock: False,
                DeviceAttributes.mode: 0,
                DeviceAttributes.fan_speed: 0,
                DeviceAttributes.oscillate: False,
                DeviceAttributes.oscillation_angle: None,
                DeviceAttributes.tilting_angle: None,
                DeviceAttributes.oscillation_mode: None,
            })
        self._default_speed_count = 3
        self._speed_count = self._default_speed_count
        self.set_customize(customize)

    @property
    def speed_count(self):
        return self._speed_count

    @property
    def oscillation_angles(self):
        return MideaFADevice._oscillation_angles

    @property
    def tilting_angles(self):
        return MideaFADevice._tilting_angles

    @property
    def oscillation_modes(self):
        return MideaFADevice._oscillation_modes

    @property
    def preset_modes(self):
        return self._modes

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageFAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.oscillation_angle:
                    if value < len(MideaFADevice._oscillation_angles):
                        self._attributes[status] = MideaFADevice._oscillation_angles[value]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.tilting_angle:
                    if value < len(MideaFADevice._tilting_angles):
                        self._attributes[status] = MideaFADevice._tilting_angles[value]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.oscillation_mode:
                    if value < len(MideaFADevice._oscillation_modes):
                        self._attributes[status] = MideaFADevice._oscillation_modes[value]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.mode:
                    if value < len(MideaFADevice._modes):
                        self._attributes[status] = MideaFADevice._modes[value]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.power:
                    self._attributes[status] = value
                    if not value:
                        self._attributes[DeviceAttributes.fan_speed] = 0
                elif status == DeviceAttributes.fan_speed and not self._attributes[DeviceAttributes.power]:
                    self._attributes[status] = 0
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_oscillation(self, attr, value):
        message = None
        if self._attributes[attr] != value:
            if attr == DeviceAttributes.oscillate:
                message = MessageSet(self._protocol_version, self.subtype)
                message.oscillate = value
                if value:
                    message.oscillation_angle = 3  # 90
                    message.oscillation_mode = 1  # Oscillation
            elif attr == DeviceAttributes.oscillation_mode and \
                    (value in MideaFADevice._oscillation_modes or not value):
                message = MessageSet(self._protocol_version, self.subtype)
                if value == "Off" or not value:
                    message.oscillate = False
                else:
                    message.oscillate = True
                    message.oscillation_mode = MideaFADevice._oscillation_modes.index(value)
                    if value == "Oscillation":
                        if self._attributes[DeviceAttributes.oscillation_angle] == "Off":
                            message.oscillation_angle = 3  # 90
                        else:
                            message.oscillation_angle = MideaFADevice._oscillation_angles.index(
                                self._attributes[DeviceAttributes.oscillation_angle]
                            )
                    elif value == "Tilting":
                        if self._attributes[DeviceAttributes.tilting_angle] == "Off":
                            message.tilting_angle = 3  # 90
                        else:
                            message.tilting_angle = MideaFADevice._tilting_angles.index(
                                self._attributes[DeviceAttributes.tilting_angle]
                            )
                    else:
                        if self._attributes[DeviceAttributes.oscillation_angle] == "Off":
                            message.oscillation_angle = 3  # 90
                        else:
                            message.oscillation_angle = MideaFADevice._oscillation_angles.index(
                                self._attributes[DeviceAttributes.oscillation_angle]
                            )
                        if self._attributes[DeviceAttributes.tilting_angle] == "Off":
                            message.tilting_angle = 3  # 90
                        else:
                            message.tilting_angle = MideaFADevice._tilting_angles.index(
                                self._attributes[DeviceAttributes.tilting_angle]
                            )
            elif attr == DeviceAttributes.oscillation_angle and \
                    (value in MideaFADevice._oscillation_angles or not value):
                message = MessageSet(self._protocol_version, self.subtype)
                if value == "Off" or not value:
                    if self._attributes[DeviceAttributes.tilting_angle] == "Off":
                        message.oscillate = False
                    else:
                        message.oscillate = True
                        message.oscillation_mode = 2
                        message.tilting_angle = MideaFADevice._tilting_angles.index(
                            self._attributes[DeviceAttributes.tilting_angle]
                        )
                else:
                    message.oscillation_angle = MideaFADevice._oscillation_angles.index(value)
                    message.oscillate = True
                    if self._attributes[DeviceAttributes.tilting_angle] == "Off":
                        message.oscillation_mode = 1
                    elif self._attributes[DeviceAttributes.oscillation_mode] == "Tilting":
                        message.oscillation_mode = 6
                        message.tilting_angle = MideaFADevice._tilting_angles.index(
                            self._attributes[DeviceAttributes.tilting_angle]
                        )
            elif attr == DeviceAttributes.tilting_angle and \
                    (value in MideaFADevice._tilting_angles or not value):
                message = MessageSet(self._protocol_version, self.subtype)
                if value == "Off" or not value:
                    if self._attributes[DeviceAttributes.oscillation_angle] == "Off":
                        message.oscillate = False
                    else:
                        message.oscillate = True
                        message.oscillation_mode = 1
                        message.oscillation_angle = MideaFADevice._oscillation_angles.index(
                            self._attributes[DeviceAttributes.oscillation_angle]
                        )
                else:
                    message.tilting_angle = MideaFADevice._tilting_angles.index(value)
                    message.oscillate = True
                    if self._attributes[DeviceAttributes.oscillation_angle] == "Off":
                        message.oscillation_mode = 2
                    elif self._attributes[DeviceAttributes.oscillation_mode] == "Oscillation":
                        message.oscillation_mode = 6
                        message.oscillation_angle = MideaFADevice._oscillation_angles.index(
                            self._attributes[DeviceAttributes.oscillation_angle]
                        )
        return message

    def set_attribute(self, attr, value):
        message = None
        if attr in [
            DeviceAttributes.oscillate,
            DeviceAttributes.oscillation_mode,
            DeviceAttributes.oscillation_angle,
            DeviceAttributes.tilting_angle
        ]:
            message = self.set_oscillation(attr, value)
        elif attr == DeviceAttributes.fan_speed and value > 0 and \
                not self._attributes[DeviceAttributes.power]:
            message = MessageSet(self._protocol_version, self.subtype)
            message.fan_speed = value
            message.power = True
        elif attr == DeviceAttributes.mode:
            if value in MideaFADevice._modes:
                message = MessageSet(self._protocol_version, self.subtype)
                message.mode = MideaFADevice._modes.index(value)
        elif not (attr == DeviceAttributes.fan_speed and value == 0):
            message = MessageSet(self._protocol_version, self.subtype)
            setattr(message, str(attr), value)
        if message is not None:
            self.build_send(message)

    def turn_on(self, fan_speed=None, mode=None):
        message = MessageSet(self._protocol_version, self.subtype)
        message.power = True
        if fan_speed is not None:
            message.fan_speed = fan_speed
        if mode is None:
            message.mode = mode
        self.build_send(message)

    def set_customize(self, customize):
        self._speed_count = self._default_speed_count
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "speed_count" in params:
                    self._speed_count = params.get("speed_count")
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"speed_count": self._speed_count})


class MideaAppliance(MideaFADevice):
    pass
