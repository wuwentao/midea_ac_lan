import logging
from typing import Any, cast

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION

if (MAJOR_VERSION, MINOR_VERSION) >= (2023, 9):
    from homeassistant.helpers.device_registry import DeviceInfo
else:
    from homeassistant.helpers.entity import DeviceInfo

from homeassistant.helpers.entity import Entity
from midealocal.device import MideaDevice

from .const import DOMAIN
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


class MideaEntity(Entity):
    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        self._device = device
        self._device.register_update(self.update_state)
        self._config = cast(dict, MIDEA_DEVICES[self._device.device_type]["entities"])[
            entity_key
        ]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._device_name = self._device.name

    @property
    def device(self) -> Any:
        return self._device

    @property
    def device_info(self) -> DeviceInfo:
        return {
            "manufacturer": "Midea",
            "model": f"{MIDEA_DEVICES[self._device.device_type]['name']} "
            f"{self._device.model}"
            f" ({self._device.subtype})",
            "identifiers": {(DOMAIN, self._device.device_id)},  # type: ignore[arg-type]
            "name": self._device_name,
        }

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def name(self) -> str:
        return (
            f"{self._device_name} {self._config.get('name')}"
            if "name" in self._config
            else self._device_name
        )

    @property
    def available(self) -> bool:
        return bool(self._device.available)

    @property
    def icon(self) -> str:
        return cast(str, self._config.get("icon"))

    def update_state(self, status: Any) -> None:
        if self._entity_key in status or "available" in status:
            self.schedule_update_ha_state()
