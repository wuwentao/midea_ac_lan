import logging
from typing import cast

from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


class MideaEntity(Entity):
    def __init__(self, device, entity_key: str):
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
    def device(self):
        return self._device

    @property
    def device_info(self):
        return {
            "manufacturer": "Midea",
            "model": f"{MIDEA_DEVICES[self._device.device_type]['name']} "
            f"{self._device.model}"
            f" ({self._device.subtype})",
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device_name,
        }

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return (
            f"{self._device_name} {self._config.get('name')}"
            if "name" in self._config
            else self._device_name
        )

    @property
    def available(self):
        return self._device.available

    @property
    def icon(self):
        return self._config.get("icon")

    def update_state(self, status):
        if self._entity_key in status or "available" in status:
            try:
                self.schedule_update_ha_state()
            except Exception as e:
                _LOGGER.debug(
                    f"Entity {self.entity_id} update_state {repr(e)}, status = {status}"
                )
