import logging
from .message import (
    MessageQuery,
    MessageFBResponse,
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
    heating_level = "heating_level"
    target_temperature = "target_temperature"
    current_temperature = "current_temperature"
    child_lock = "child_lock"


class MideaFBDevice(MideaDevice):
    _modes = {0x01: "Auto", 0x02: "ECO", 0x03: "Sleep",
              0x04: "Anti-freezing", 0x05: "Comfort", 0x06: "Constant-temperature",
              0x07: "Normal", 0x08: "Fast-heating", 0x10: "Standby"}

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
            device_type=0xFB,
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
                DeviceAttributes.heating_level: 0,
                DeviceAttributes.target_temperature: None,
                DeviceAttributes.current_temperature: None,
                DeviceAttributes.child_lock: False,
            })

    @property
    def modes(self):
        return list(MideaFBDevice._modes.values())

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageFBResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                value = getattr(message, str(status))
                if status == DeviceAttributes.mode:
                    if value in MideaFBDevice._modes.keys():
                        self._attributes[status] = MideaFBDevice._modes.get(value)
                    else:
                        self._attributes[status] = None
                else:
                    self._attributes[status] = value
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.mode:
            message = MessageSet(self._protocol_version, self.subtype)
            if value in MideaFBDevice._modes.values():
                message.mode = list(MideaFBDevice._modes.keys())[
                    list(MideaFBDevice._modes.values()).index(value)
                ]
        else:
            message = MessageSet(self._protocol_version, self.subtype)
            setattr(message, str(attr), value)
        self.build_send(message)


class MideaAppliance(MideaFBDevice):
    pass
