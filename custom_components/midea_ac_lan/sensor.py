"""Sensor for Midea Lan."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_SENSORS, Platform
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.util import dt as dt_util

from .ac_bb_diagnostics import (
    BB_ENERGY_ATTRIBUTES,
    restore_ac_bb_energy,
)
from .ac_c1_diagnostics import supports_ac_diagnostic_attribute
from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType
    from midealocal.device import MideaDevice


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
        if config.get("ac_diagnostic") and not supports_ac_diagnostic_attribute(
            entity_key,
            device.device_type,
            device.model,
            device.subtype,
        ):
            continue
        sensor_class = (
            MideaBBDiagnosticEnergySensor
            if entity_key in BB_ENERGY_ATTRIBUTES
            else MideaSensor
        )
        sensors.append(sensor_class(device, entity_key))
    async_add_entities(sensors)


class MideaSensor(MideaEntity, SensorEntity):
    """Represent a Midea  sensor."""

    @property
    def native_value(self) -> StateType:
        """Return entity value."""
        return cast("StateType", self._device.get_attribute(self._entity_key))

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return device class."""
        return cast("SensorDeviceClass", self._config.get("device_class"))

    @property
    def state_class(self) -> SensorStateClass | None:
        """Return state state."""
        return cast("SensorStateClass | None", self._config.get("state_class"))

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        return cast("str | None", self._config.get("unit"))

    @property
    def capability_attributes(self) -> dict[str, Any] | None:
        """Return capabilities."""
        return {"state_class": self.state_class} if self.state_class else {}


class MideaBBDiagnosticEnergySensor(RestoreEntity, MideaSensor):
    """Represent a restorable cumulative BB diagnostics energy sensor."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize a restorable BB diagnostics energy sensor."""
        super().__init__(device, entity_key)

    async def async_added_to_hass(self) -> None:
        """Restore the previous cumulative energy value."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        restored_value = 0.0
        last_updated = dt_util.utcnow()
        if last_state is not None:
            last_updated = last_state.last_updated
            with suppress(TypeError, ValueError):
                restored_value = float(last_state.state)
        restore_ac_bb_energy(
            self._device,
            self._entity_key,
            restored_value,
            last_updated,
        )
        self.async_write_ha_state()
