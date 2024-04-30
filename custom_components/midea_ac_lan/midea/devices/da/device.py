import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStart,
    MessageDAResponse
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    start = "start"
    washing_data = "washing_data"
    program = "program"
    progress = "progress"
    time_remaining = "time_remaining"
    wash_time = "wash_time"
    soak_time = "soak_time"
    dehydration_time = "dehydration_time"
    dehydration_speed = "dehydration_speed"
    error_code = "error_code"
    rinse_count = "rinse_count"
    rinse_level = "rinse_level"
    wash_level = "wash_level"
    wash_strength = "wash_strength"
    softener = "softener"
    detergent = "detergent"
    

class MideaDADevice(MideaDevice):
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
            device_type=0xDA,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.start: False,
                DeviceAttributes.error_code: None,
                DeviceAttributes.washing_data: bytearray([]),
                DeviceAttributes.program: None,
                DeviceAttributes.progress: "Unknown",
                DeviceAttributes.time_remaining: None,
                DeviceAttributes.wash_time: None,
                DeviceAttributes.soak_time: None,
                DeviceAttributes.dehydration_time: None,
                DeviceAttributes.dehydration_speed: None,
                DeviceAttributes.rinse_count: None,
                DeviceAttributes.rinse_level: None,
                DeviceAttributes.wash_level: None,
                DeviceAttributes.wash_strength: None,
                DeviceAttributes.softener: None,
                DeviceAttributes.detergent: None
            })

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageDAResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        progress = ["Idle", "Spin", "Rinse", "Wash",
                    "Weight", "Unknown", "Dry", "Soak"]
        program = ["Standard", "Fast", "Blanket", "Wool",
                   "embathe", "Memory", "Child", "Down Jacket",
                   "Stir", "Mute", "Bucket Self Clean", "Air Dry"]
        speed = ["-", "Low", "Medium", "High"]
        strength = ["-", "Week", "Medium", "Strong"]
        detergent = ["No", "Less", "Medium", "More", "4",
                    "5", "6", "7", "8", "Insufficient"]
        softener = ["No", "Intelligent", "Programed", "3", "4",
                    "5", "6", "7", "8", "Insufficient"]
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                if status == DeviceAttributes.progress:
                    self._attributes[status] = progress[getattr(message, str(status))]
                elif status == DeviceAttributes.program:
                    self._attributes[status] = program[getattr(message, str(status))]
                elif status == DeviceAttributes.rinse_level:
                    temp_rinse_level = getattr(message, str(status))
                    if temp_rinse_level == 15:
                        self._attributes[status] = "-"
                    else:
                        self._attributes[status] = temp_rinse_level
                elif status == DeviceAttributes.dehydration_speed:
                    temp_speed = getattr(message, str(status))
                    if temp_speed == 15:
                        self._attributes[status] = "-"
                    else:
                        self._attributes[status] = speed[temp_speed]
                elif status == DeviceAttributes.detergent:
                    self._attributes[status] = detergent[getattr(message, str(status))]
                elif status == DeviceAttributes.softener:
                    self._attributes[status] = softener[getattr(message, str(status))]
                elif status == DeviceAttributes.wash_strength:
                    self._attributes[status] = strength[getattr(message, str(status))]
                else:
                    self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower(self._protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.start:
            message = MessageStart(self._protocol_version)
            message.start = value
            message.washing_data = self._attributes[DeviceAttributes.washing_data]
            self.build_send(message)

class MideaAppliance(MideaDADevice):
    pass
