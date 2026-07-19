"""Time for Midea Lan."""

import logging
from datetime import time
from typing import cast

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.device import MideaDevice

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up times for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    times = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] == Platform.TIME and entity_key in extra_switches:
            dev = MideaTime(device, entity_key)
            times.append(dev)
    async_add_entities(times)


class MideaTime(MideaEntity, TimeEntity):
    """Represent a Midea time entity."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea time entity init."""
        super().__init__(device, entity_key)
        # Config can specify hour/min attribute names explicitly:
        #   "hour_attr": "timing_regeneration_hour"
        #   "min_attr": "timing_regeneration_min"
        # Otherwise derive from entity_key: if it ends with "_hour",
        # use it directly and replace "_hour" with "_min" for minute.
        self._hour_attr = self._config.get("hour_attr")
        self._min_attr = self._config.get("min_attr")
        if self._hour_attr is None:
            if self._entity_key.endswith("_hour"):
                self._hour_attr = self._entity_key
                self._min_attr = self._entity_key[:-5] + "_min"
            else:
                self._hour_attr = f"{self._entity_key}_hour"
                self._min_attr = f"{self._entity_key}_min"

    @property
    def native_value(self) -> time | None:
        """Return entity value."""
        hour = self._device.get_attribute(self._hour_attr)
        minute = self._device.get_attribute(self._min_attr)
        if hour is None or minute is None:
            return None
        try:
            return time(hour=cast("int", hour), minute=cast("int", minute))
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Invalid time value for %s: hour=%s, minute=%s",
                self._entity_key,
                hour,
                minute,
            )
            return None

    def set_value(self, value: time) -> None:
        """Set entity value."""
        self._device.set_attribute(self._hour_attr, value.hour)
        self._device.set_attribute(self._min_attr, value.minute)
