from .midea_entity import MideaEntity
from .midea_devices import MIDEA_DEVICES
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_SENSORS
)
from .const import (
    DOMAIN,
    DEVICES
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_sensors = config_entry.options.get(
        CONF_SENSORS, []
    )
    sensors = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.SENSOR and entity_key in extra_sensors:
            sensor = MideaSensor(device, entity_key)
            sensors.append(sensor)
    async_add_entities(sensors)


class MideaSensor(MideaEntity, SensorEntity):
    @property
    def native_value(self):
        return self._device.get_attribute(self._entity_key)

    @property
    def device_class(self):
        return self._config.get("device_class")

    @property
    def state_class(self):
        return self._config.get("state_class")

    @property
    def native_unit_of_measurement(self):
        return self._config.get("unit")

    @property
    def capability_attributes(self):
        return {"state_class": self.state_class} if self.state_class else {}
