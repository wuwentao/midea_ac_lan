import logging
import math
from .message import (
    MessageQuery,
    MessageSet,
    Message40Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    light = "light"
    fan_speed = "fan_speed"
    direction = "direction"
    ventilation = "ventilation"
    smelly_sensor = "smelly_sensor"
    current_temperature = "current_temperature"


class Midea40Device(MideaDevice):
    _directions = ["60", "70", "80", "90", "100", "Oscillate"]

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
            device_type=0x40,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.light: False,
                DeviceAttributes.fan_speed: 0,
                DeviceAttributes.direction: False,
                DeviceAttributes.ventilation: False,
                DeviceAttributes.smelly_sensor: False,
                DeviceAttributes.current_temperature: None
            })
        self._fields = {}

    @property
    def directions(self):
        return Midea40Device._directions

    @staticmethod
    def _convert_to_midea_direction(direction):
        if direction == "Oscillate":
            result = 0xFD
        else:
            result = Midea40Device._directions.index(direction) * 10 + 60 \
                if direction in Midea40Device._directions else 0xFD
        return result

    @staticmethod
    def _convert_from_midea_direction(direction):
        if direction > 100 or direction < 60:
            result = 5
        else:
            result = math.floor((direction - 60 + 5) / 10)
        return result

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = Message40Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        self._fields = getattr(message, "fields")
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.direction:
                    self._attributes[status] = Midea40Device._directions[
                        self._convert_from_midea_direction(value)
                    ]
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr in [DeviceAttributes.light,
                    DeviceAttributes.fan_speed,
                    DeviceAttributes.direction,
                    DeviceAttributes.ventilation,
                    DeviceAttributes.smelly_sensor]:
            message = MessageSet(self._protocol_version)
            message.fields = self._fields
            message.light = self._attributes[DeviceAttributes.light]
            message.ventilation = self._attributes[DeviceAttributes.ventilation]
            message.smelly_sensor = self._attributes[DeviceAttributes.smelly_sensor]
            message.fan_speed = self._attributes[DeviceAttributes.fan_speed]
            message.direction = self._convert_to_midea_direction(self._attributes[DeviceAttributes.direction])
            if attr == DeviceAttributes.direction:
                message.direction = self._convert_to_midea_direction(value)
            elif attr == DeviceAttributes.ventilation and message.fan_speed == 2:
                message.fan_speed = 1
                message.ventilation = value
            else:
                setattr(message, str(attr), value)
            self.build_send(message)


class MideaAppliance(Midea40Device):
    pass
