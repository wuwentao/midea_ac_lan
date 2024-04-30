import logging
from .message import (
    MessageQuery,
    MessagePower,
    MessageStorage,
    MessageLock,
    Message34Response
)
try:
    from enum import StrEnum
except ImportError:
    from ...backports.enum import StrEnum
from ...core.device import MideaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    power = "power"
    status = "status"
    mode = "mode"
    additional = "additional"
    door = "door"
    rinse_aid = "rinse_aid"
    salt = "salt"
    child_lock = "child_lock"
    uv = "uv"
    dry = "dry"
    dry_status = "dry_status"
    storage = "storage"
    storage_status = "storage_status"
    time_remaining = "time_remaining"
    progress = "progress"
    storage_remaining = "storage_remaining"
    temperature = "temperature"
    humidity = "humidity"
    waterswitch = "waterswitch"
    water_lack = "water_lack"
    error_code = "error_code"
    softwater = "softwater"
    wrong_operation = "wrong_operation"
    bright = "bright"


class Midea34Device(MideaDevice):
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
            device_type=0x34,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            attributes={
                DeviceAttributes.power: False,
                DeviceAttributes.status: None,
                DeviceAttributes.mode: 0,
                DeviceAttributes.additional: 0,
                DeviceAttributes.uv: False,
                DeviceAttributes.dry: False,
                DeviceAttributes.dry_status: False,
                DeviceAttributes.door: False,
                DeviceAttributes.rinse_aid: False,
                DeviceAttributes.salt: False,
                DeviceAttributes.child_lock: False,
                DeviceAttributes.storage: False,
                DeviceAttributes.storage_status: False,
                DeviceAttributes.time_remaining: None,
                DeviceAttributes.progress: None,
                DeviceAttributes.storage_remaining: None,
                DeviceAttributes.temperature: None,
                DeviceAttributes.humidity: None,
                DeviceAttributes.waterswitch: False,
                DeviceAttributes.water_lack: False,
                DeviceAttributes.error_code: None,
                DeviceAttributes.softwater: 0,
                DeviceAttributes.wrong_operation: None,
                DeviceAttributes.bright: 0
            })
        self._modes = {
            0x0: "Neutral Gear",        # BYTE_MODE_NEUTRAL_GEAR
            0x1: "Auto",                # BYTE_MODE_AUTO_WASH
            0x2: "Heavy",               # BYTE_MODE_STRONG_WASH
            0x3: "Normal",              # BYTE_MODE_STANDARD_WASH
            0x4: "Energy Saving",       # BYTE_MODE_ECO_WASH
            0x5: "Delicate",            # BYTE_MODE_GLASS_WASH
            0x6: "Hour",                # BYTE_MODE_HOUR_WASH
            0x7: "Quick",               # BYTE_MODE_FAST_WASH
            0x8: "Rinse",               # BYTE_MODE_SOAK_WASH
            0x9: "90min",               # BYTE_MODE_90MIN_WASH
            0xA: "Self Clean",          # BYTE_MODE_SELF_CLEAN
            0xB: "Fruit Wash",          # BYTE_MODE_FRUIT_WASH
            0xC: "Self Define",         # BYTE_MODE_SELF_DEFINE
            0xD: "Germ",                # BYTE_MODE_GERM ???
            0xE: "Bowl Wash",           # BYTE_MODE_BOWL_WASH
            0xF: "Kill Germ",           # BYTE_MODE_KILL_GERM
            0x10: "Sea Food Wash",      # BYTE_MODE_SEA_FOOD_WASH
            0x12: "Hot Pot Wash",       # BYTE_MODE_HOT_POT_WASH
            0x13: "Quiet",              # BYTE_MODE_QUIET_NIGHT_WASH
            0x14: "Less Wash",          # BYTE_MODE_LESS_WASH
            0x16: "Oil Net Wash",       # BYTE_MODE_OIL_NET_WASH
            0x19: "Cloud Wash"          # BYTE_MODE_CLOUD_WASH
        }
        self._status = ["Off", "Idle", "Delay", "Running", "Error"]
        self._progress = ["Idle", "Pre-wash", "Wash", "Rinse", "Dry", "Complete"]

    def build_query(self):
        return [MessageQuery(self._protocol_version)]

    def process_message(self, msg):
        message = Message34Response(msg)
        _LOGGER.debug(f"[{self.device_id}] Received: {message}")
        new_status = {}
        for status in self._attributes.keys():
            if hasattr(message, str(status)):
                if status == DeviceAttributes.status:
                    v = getattr(message, str(status))
                    if v < len(self._status):
                        self._attributes[status] = self._status[v]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.progress:
                    v = getattr(message, str(status))
                    if v < len(self._progress):
                        self._attributes[status] = self._progress[v]
                    else:
                        self._attributes[status] = None
                elif status == DeviceAttributes.mode:
                    v = getattr(message, str(status))
                    self._attributes[status] = self._modes[v]
                else:
                    self._attributes[status] = getattr(message, str(status))
                new_status[str(status)] = self._attributes[status]
        return new_status

    def set_attribute(self, attr, value):
        if attr == DeviceAttributes.power:
            message = MessagePower(self._protocol_version)
            message.power = value
            self.build_send(message)
        elif attr == DeviceAttributes.child_lock:
            message = MessageLock(self._protocol_version)
            message.lock = value
            self.build_send(message)
        elif attr == DeviceAttributes.storage:
            message = MessageStorage(self._protocol_version)
            message.storage = value
            self.build_send(message)


class MideaAppliance(Midea34Device):
    pass
