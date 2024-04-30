import logging
from .message import (
    MessageQuery,
    MessageE8Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    status = "status"
    time_remaining = "time_remaining"
    keep_warm_remaining = "keep_warm_remaining"
    working_time = "working_time"
    target_temperature = "target_temperature"
    current_temperature = "current_temperature"
    finished = "finished"
    water_shortage = "water_shortage"


class MideaE8Device(MideaDevice):
    _status = {
        0x00: "Standby", 0x01: "Delay", 0x02: "Working",
        0x03: "Paused", 0x04: "Keep-Warming", 0xFF: "Error"
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
            device_type=0xB1,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.status: None,
                DeviceAttributes.time_remaining: None,
                DeviceAttributes.keep_warm_remaining: None,
                DeviceAttributes.working_time: None,
                DeviceAttributes.target_temperature: None,
                DeviceAttributes.current_temperature: None,
                DeviceAttributes.finished: None,
                DeviceAttributes.water_shortage: None,
            })

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageE8Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.status:
                    if value in MideaE8Device._status.keys():
                        self._attributes[DeviceAttributes.status] = MideaE8Device._status.get(value)
                    else:
                        self._attributes[DeviceAttributes.status] = None
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        pass


class MideaAppliance(MideaE8Device):
    pass
