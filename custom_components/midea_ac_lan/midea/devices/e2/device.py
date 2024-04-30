import logging
import json
from .message import (
    MessageQuery,
    MessageSet,
    MessageE2Response,
    MessagePower,
    MessageNewProtocolSet
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    heating = "heating"
    keep_warm = "keep_warm"
    protection = "protection"
    current_temperature = "current_temperature"
    target_temperature = "target_temperature"
    whole_tank_heating = "whole_tank_heating"
    variable_heating = "variable_heating"
    heating_time_remaining = "heating_time_remaining"
    water_consumption = "water_consumption"
    heating_power = "heating_power"


class MideaE2Device(MideaDevice):
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
            device_type=0xE2,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.heating: False,
                DeviceAttributes.keep_warm: False,
                DeviceAttributes.protection: False,
                DeviceAttributes.current_temperature: None,
                DeviceAttributes.target_temperature: 40,
                DeviceAttributes.whole_tank_heating: False,
                DeviceAttributes.variable_heating: False,
                DeviceAttributes.heating_time_remaining: 0,
                DeviceAttributes.water_consumption: None,
                DeviceAttributes.heating_power: None
            })
        self._default_old_protocol = "auto"
        self._old_protocol = self._default_old_protocol
        self.set_customize(customize)

    def old_protocol(self):
        return self.subtype <= 82 or self.subtype == 85 or self.subtype == 36353

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = MessageE2Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = getattr(message, str(status))
        return new_status

    def make_message_set(self):
        message = MessageSet(self._protocol_version)
        message.protection = self._attributes[DeviceAttributes.protection]
        message.whole_tank_heating = self._attributes[DeviceAttributes.whole_tank_heating]
        message.target_temperature = self._attributes[DeviceAttributes.target_temperature]
        message.variable_heating = self._attributes[DeviceAttributes.variable_heating]
        return message

    def set_attribute(self, attr, value):
        if attr not in [DeviceAttributes.heating,
                        DeviceAttributes.keep_warm,
                        DeviceAttributes.current_temperature]:
            if self._old_protocol is not None and self._old_protocol != "auto":
                old_protocol = self._old_protocol
            else:
                old_protocol = self.old_protocol()
            if attr == DeviceAttributes.power:
                message = MessagePower(self._protocol_version)
                message.power = value
            elif old_protocol:
                message = self.make_message_set()
                setattr(message, str(attr), value)
            else:
                message = MessageNewProtocolSet(self._protocol_version)
                setattr(message, str(attr), value)
            self.build_send(message)

    def set_customize(self, customize):
        self._old_protocol = self._default_old_protocol
        if customize and len(customize) > 0:
            try:
                params = json.loads(customize)
                if params and "old_protocol" in params:
                    self._old_protocol = params.get("old_protocol")
            except Exception as e:
                _LOGGER.error(f"[{self.device_id}] Set customize error: {repr(e)}")
            self.update_all({"old_protocol": self._old_protocol})


class MideaAppliance(MideaE2Device):
    pass
