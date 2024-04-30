import logging
import math
from .message import (
    MessageQuery,
    MessageSet,
    Message26Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    main_light = "main_light"
    night_light = "night_light"
    mode = "mode"
    direction = "direction"
    current_humidity = "current_humidity"
    current_radar = "current_radar"
    current_temperature = "current_temperature"


class Midea26Device(MideaDevice):
    _modes = ["Off", "Heat(high)", "Heat(low)", "Bath", "Blow", "Ventilation", "Dry"]
    _directions = ["60", "70", "80", "90", "100", "110", "120", "Oscillate"]

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
            device_type=0x26,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.main_light: False,
                DeviceAttributes.night_light: False,
                DeviceAttributes.mode: None,
                DeviceAttributes.direction: None,
                DeviceAttributes.current_humidity: None,
                DeviceAttributes.current_radar: None,
                DeviceAttributes.current_temperature: None
            })
        self._fields = {}

    @staticmethod
    def _convert_to_midea_direction(direction):
        if direction == "Oscillate":
            result = 0xFD
        else:
            result = Midea26Device._directions.index(direction) * 10 + 60 \
                if direction in Midea26Device._directions else 0xFD
        return result

    @staticmethod
    def _convert_from_midea_direction(direction):
        if direction > 120 or direction < 60:
            result = 7
        else:
            result = math.floor((direction - 60 + 5) / 10)
        return result

    @property
    def preset_modes(self):
        return Midea26Device._modes

    @property
    def directions(self):
        return Midea26Device._directions

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = Message26Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        self._fields = getattr(message, "fields")
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.mode:
                    self._attributes[status] = Midea26Device._modes[value]
                elif status == DeviceAttributes.direction:
                    self._attributes[status] = Midea26Device._directions[
                        self._convert_from_midea_direction(value)
                    ]
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.main_light,
                    DeviceAttributes.night_light,
                    DeviceAttributes.mode,
                    DeviceAttributes.direction
                    ]:
            message = MessageSet(self._protocol_version)
            message.fields = self._fields
            message.main_light = self._attributes[DeviceAttributes.main_light]
            message.night_light = self._attributes[DeviceAttributes.night_light]
            message.mode = Midea26Device._modes.index(self._attributes[DeviceAttributes.mode])
            message.direction = self._convert_to_midea_direction(self._attributes[DeviceAttributes.direction])
            if attr in [
                DeviceAttributes.main_light,
                DeviceAttributes.night_light
            ]:
                message.main_light = False
                message.night_light = False
                setattr(message, str(attr), value)
            elif attr == DeviceAttributes.mode:
                message.mode = Midea26Device._modes.index(value)
            elif attr == DeviceAttributes.direction:
                message.direction = self._convert_to_midea_direction(value)
            self.build_send(message)


class MideaAppliance(Midea26Device):
    pass
