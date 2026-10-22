"""Button for Midea Lan."""

from typing import Any, cast

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealan.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_device
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    buttons = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] == Platform.BUTTON
            and supports_device(device.model, device.subtype, config)
            and (config.get("default") or entity_key in extra_switches)
        ):
            required_attribute = config.get("required_attribute")
            if (
                required_attribute is not None
                and required_attribute not in device.attributes
            ):
                continue
            buttons.append(MideaButton(device, entity_key))
    async_add_entities(buttons)


class MideaButton(MideaEntity, ButtonEntity):
    """Represent a Midea button."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize Midea button."""
        super().__init__(device, entity_key)
        self._power_attribute = self._config.get("available_power_attribute")

    @property
    def available(self) -> bool:
        """Whether the entity is available."""
        if not super().available:
            return False
        return not self._power_attribute or bool(
            self._device.get_attribute(self._power_attribute),
        )

    def press(self) -> None:
        """Press button: write the configured attribute or status trigger."""
        if "press_value" in self._config:
            self._device.set_attribute(
                self._config.get("attribute", self._entity_key),
                self._config["press_value"],
            )
        else:
            self._device.set_attribute("status", self._config["press_status"])

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Update entity state."""
        super().update_state(status)
        if self.hass and self._power_attribute in status:
            self.schedule_update_if_running()
