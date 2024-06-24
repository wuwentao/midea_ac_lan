"""Number for Midea Lan."""

from typing import Any, cast

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.device import MideaDevice

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up numbers for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    numbers = []
    for entity_key, config in cast(
        dict,
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] == Platform.NUMBER and entity_key in extra_switches:
            dev = MideaNumber(device, entity_key)
            numbers.append(dev)
    async_add_entities(numbers)


class MideaNumber(MideaEntity, NumberEntity):
    """Represent a Midea number sensor."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea number sensor init."""
        super().__init__(device, entity_key)
        self._max_value = self._config.get("max")
        self._min_value = self._config.get("min")
        self._step_value = self._config.get("step")

    @property
    def native_min_value(self) -> float:
        """Return minimum value."""
        return cast(
            float,
            (
                self._min_value
                if isinstance(self._min_value, int)
                else (
                    self._device.get_attribute(attr=self._min_value)
                    if self._device.get_attribute(attr=self._min_value)
                    else getattr(self._device, self._min_value)
                )
            ),
        )

    @property
    def native_max_value(self) -> float:
        """Return maximum value."""
        return cast(
            float,
            (
                self._max_value
                if isinstance(self._max_value, int)
                else (
                    self._device.get_attribute(attr=self._max_value)
                    if self._device.get_attribute(attr=self._max_value)
                    else getattr(self._device, self._max_value)
                )
            ),
        )

    @property
    def native_step(self) -> float:
        """Return step value."""
        return cast(
            float,
            (
                self._step_value
                if isinstance(self._step_value, int)
                else (
                    self._device.get_attribute(attr=self._step_value)
                    if self._device.get_attribute(attr=self._step_value)
                    else getattr(self._device, self._step_value)
                )
            ),
        )

    @property
    def native_value(self) -> float:
        """Return value."""
        return cast(float, self._device.get_attribute(self._entity_key))

    def set_native_value(self, value: Any) -> None:  # noqa: ANN401
        """Set value."""
        self._device.set_attribute(self._entity_key, value)
