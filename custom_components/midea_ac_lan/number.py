"""Number for Midea Lan."""

from typing import Any, cast

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealan.device import MideaDevice

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
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] != Platform.NUMBER or entity_key not in extra_switches:
            continue
        required_attribute = config.get("required_attribute")
        if (
            required_attribute is not None
            and required_attribute not in device.attributes
        ):
            continue
        numbers.append(MideaNumber(device, entity_key))
    async_add_entities(numbers)


class MideaNumber(MideaEntity, NumberEntity):
    """Represent a Midea number sensor."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea number sensor init."""
        super().__init__(device, entity_key)
        self._max_value = self._config.get("max")
        self._min_value = self._config.get("min")
        self._step_value = self._config.get("step")

    def _resolve_bound(self, bound: Any) -> float:  # ruff:ignore[any-type]
        """Resolve a min/max/step config value to a concrete number.

        A numeric literal is used as-is. Otherwise the value is treated as an
        attribute name: prefer the device attribute of that name, falling back
        to a same-named device property populated by ``set_customize``.

        Returns
        -------
        The resolved bound as a float.

        """
        if isinstance(bound, (int, float)):
            return cast("float", bound)
        # `bound` is an attribute name. Use `is not None` (not truthiness) so a
        # legitimate 0 is not treated as "missing", and read the attribute once.
        value = self._device.get_attribute(attr=bound)
        if value is None:
            value = getattr(self._device, bound)
        return cast("float", value)

    @property
    def native_min_value(self) -> float:
        """Minimum value allowed."""
        return self._resolve_bound(self._min_value)

    @property
    def native_max_value(self) -> float:
        """Maximum value allowed."""
        return self._resolve_bound(self._max_value)

    @property
    def native_step(self) -> float:
        """Step value between allowed values."""
        return self._resolve_bound(self._step_value)

    @property
    def native_value(self) -> float:
        """Native value of the entity."""
        return cast("float", self._device.get_attribute(self._entity_key))

    def set_native_value(self, value: Any) -> None:  # ruff:ignore[any-type]
        """Set value."""
        self._device.set_attribute(self._entity_key, value)
