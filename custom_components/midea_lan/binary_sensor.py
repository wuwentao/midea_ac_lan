"""Binary sensor for Midea Lan."""

from typing import cast

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_sensors = config_entry.options.get(CONF_SENSORS, [])
    binary_sensors = []
    for entity_key, config in cast(
        dict,
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] == Platform.BINARY_SENSOR and entity_key in extra_sensors:
            sensor = MideaBinarySensor(device, entity_key)
            binary_sensors.append(sensor)
    async_add_entities(binary_sensors)


class MideaBinarySensor(MideaEntity, BinarySensorEntity):
    """Represent a Midea binary sensor."""

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Return device class."""
        return cast(BinarySensorDeviceClass, self._config.get("device_class"))

    @property
    def is_on(self) -> bool:
        """Return true if sensor state is on."""
        return cast(bool, self._device.get_attribute(self._entity_key))
