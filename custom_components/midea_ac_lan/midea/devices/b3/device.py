import logging
from .message import (
    MessageQuery,
    MessageB3Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    top_compartment_status = "top_compartment_status"
    top_compartment_mode = "top_compartment_mode"
    top_compartment_temperature = "top_compartment_temperature"
    top_compartment_remaining = "top_compartment_remaining"
    top_compartment_door = "top_compartment_door"
    top_compartment_preheating = "top_compartment_preheating"
    top_compartment_cooling = "top_compartment_cooling"
    middle_compartment_status = "middle_compartment_status"
    middle_compartment_mode = "middle_compartment_mode"
    middle_compartment_temperature = "middle_compartment_temperature"
    middle_compartment_remaining = "middle_compartment_remaining"
    middle_compartment_door = "middle_compartment_door"
    middle_compartment_preheating = "middle_compartment_preheating"
    middle_compartment_cooling = "middle_compartment_cooling"
    bottom_compartment_status = "bottom_compartment_status"
    bottom_compartment_mode = "bottom_compartment_mode"
    bottom_compartment_temperature = "bottom_compartment_temperature"
    bottom_compartment_remaining = "bottom_compartment_remaining"
    bottom_compartment_door = "bottom_compartment_door"
    bottom_compartment_preheating = "bottom_compartment_preheating"
    bottom_compartment_cooling = "bottom_compartment_cooling"
    lock = "lock"


class MideaB2Device(MideaDevice):
    _status = {
        0x00: "Off", 0x01: "Standby", 0x02: "Working",
        0x03: "Delay", 0x04: "Finished"
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
            device_type=0xB3,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.top_compartment_status: None,
                DeviceAttributes.top_compartment_mode: None,
                DeviceAttributes.top_compartment_temperature: None,
                DeviceAttributes.top_compartment_remaining: None,
                DeviceAttributes.top_compartment_door: False,
                DeviceAttributes.top_compartment_preheating: False,
                DeviceAttributes.top_compartment_cooling: False,
                DeviceAttributes.middle_compartment_status: None,
                DeviceAttributes.middle_compartment_mode: None,
                DeviceAttributes.middle_compartment_temperature: None,
                DeviceAttributes.middle_compartment_remaining: None,
                DeviceAttributes.middle_compartment_door: False,
                DeviceAttributes.middle_compartment_preheating: False,
                DeviceAttributes.middle_compartment_cooling: False,
                DeviceAttributes.bottom_compartment_status: None,
                DeviceAttributes.bottom_compartment_mode: None,
                DeviceAttributes.bottom_compartment_temperature: None,
                DeviceAttributes.bottom_compartment_remaining: None,
                DeviceAttributes.bottom_compartment_door: False,
                DeviceAttributes.bottom_compartment_preheating: False,
                DeviceAttributes.bottom_compartment_cooling: False,
                DeviceAttributes.lock: False,
            })

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageB3Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status in [
                    DeviceAttributes.top_compartment_status,
                    DeviceAttributes.middle_compartment_status,
                    DeviceAttributes.bottom_compartment_status
                ]:
                    if value in MideaB2Device._status.keys():
                        self._attributes[status] = MideaB2Device._status.get(value)
                    else:
                        self._attributes[status] = None
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        pass


class MideaAppliance(MideaB2Device):
    pass
