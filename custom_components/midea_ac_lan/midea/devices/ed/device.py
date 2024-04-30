import logging
from .message import (
    MessageQuery,
    MessageEDResponse,
    MessageNewSet,
    MessageOldSet
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    water_consumption = "water_consumption"
    in_tds = "in_tds"
    out_tds = "out_tds"
    filter1 = "filter1"
    filter2 = "filter2"
    filter3 = "filter3"
    life1 = "life1"
    life2 = "life2"
    life3 = "life3"
    child_lock = "child_lock"


class MideaEDDevice(MideaDevice):

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
            device_type=0xED,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.water_consumption: None,
                DeviceAttributes.in_tds: None,
                DeviceAttributes.out_tds: None,
                DeviceAttributes.filter1: None,
                DeviceAttributes.filter2: None,
                DeviceAttributes.filter3: None,
                DeviceAttributes.life1: None,
                DeviceAttributes.life2: None,
                DeviceAttributes.life3: None,
                DeviceAttributes.child_lock: False
            })
        self._device_class = 0

    def _use_new_set(self):
        return True # if (self.sub_type > 342 or self.sub_type == 340) else False

    def build_query(self):
        return [
            MessageQuery(self._protocol_version, self._device_class)
        ]

    def process_message(self, msg):
        message = MessageEDResponse(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        if hasattr(message, "device_class"):
            self._device_class = message.device_class
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                new_status[str(status)] = getattr(message, str(status))
                self._attributes[status] = getattr(message, str(status))
        return new_status

    def set_attribute(self, attr, value):
        message = None
        if self._use_new_set():
            if attr in [
                DeviceAttributes.power,
                DeviceAttributes.child_lock
            ]:
                message = MessageNewSet(self._protocol_version)
        else:
            if attr in []:
                message = MessageOldSet(self._protocol_version)
        if message is not None:
            setattr(message, str(attr), value)
            self.build_send(message)


class MideaAppliance(MideaEDDevice):
    pass
