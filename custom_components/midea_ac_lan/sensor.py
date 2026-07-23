"""Sensor for Midea Lan."""

from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

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
    sensors = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] != Platform.SENSOR or entity_key not in extra_sensors:
            continue
        required_attribute = config.get("required_attribute")
        if (
            required_attribute is not None
            and required_attribute not in device.attributes
        ):
            continue
        sensors.append(MideaSensor(device, entity_key))
    async_add_entities(sensors)


class MideaSensor(MideaEntity, SensorEntity):
    """Represent a Midea  sensor."""

    @property
    def native_value(self) -> StateType:
        """Return entity value."""
        value = self._device.get_attribute(self._entity_key)
        # If an options mapping exists, translate the raw value to its enum key.
        options = self._config.get("options")
        if options is not None and isinstance(value, int):
            # For an enum sensor an unmapped value is not a valid state, so
            # report it as unknown (None) instead of leaking the raw int.
            return cast("StateType", options.get(value))
        return cast("StateType", value)

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class."""
        return cast("SensorDeviceClass", self._config.get("device_class"))

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return state state."""
        return cast("SensorStateClass | None", self._config.get("state_class"))

    @property
    def options(self) -> list[str] | None:
        """Return the list of possible states for an enum sensor."""
        if self.device_class != SensorDeviceClass.ENUM:
            return None
        options = self._config.get("options")
        return list(options.values()) if options else None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        return cast("str | None", self._config.get("unit"))

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested number of decimal digits for display."""
        return cast("int | None", self._config.get("suggested_display_precision"))

    @property
    def capability_attributes(self) -> dict[str, Any] | None:
        """Return capabilities."""
        if self.options is not None:
            return {"options": self.options}
        return {"state_class": self.state_class} if self.state_class else {}
