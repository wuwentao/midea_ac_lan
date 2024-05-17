from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import Platform, CONF_DEVICE_ID, CONF_SENSORS
from .const import (
    DOMAIN,
    DEVICES
)
from .midea_entity import MideaEntity
from .midea_devices import MIDEA_DEVICES


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_sensors = config_entry.options.get(
        CONF_SENSORS, []
    )
    binary_sensors = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.BINARY_SENSOR and entity_key in extra_sensors:
            sensor = MideaSensor(device, entity_key)
            binary_sensors.append(sensor)
    async_add_entities(binary_sensors)


class MideaSensor(MideaEntity, BinarySensorEntity):
    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def is_on(self):
        return self._device.get_attribute(self._entity_key)
