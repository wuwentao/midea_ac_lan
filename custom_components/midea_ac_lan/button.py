"""Button for Midea Lan."""

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_model
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

if TYPE_CHECKING:
    from midealocal.devices.e1 import MideaE1Device


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
            and supports_model(device.model, config)
            and (config.get("default") or entity_key in extra_switches)
        ):
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
        """Return entity availability."""
        if not super().available:
            return False
        if self._power_attribute and not self._device.get_attribute(
            self._power_attribute,
        ):
            return False
        return self._get_current_mode_code() not in {None, 0}

    def press(self) -> None:
        """Press button."""
        if self._config.get("set_message") == "e1_start":
            self._press_e1_start()

    def _press_e1_start(self) -> None:
        """Start E1 dishwasher using the current mode.

        Raises
        ------
        ValueError
            If the current dishwasher mode is not supported.

        """
        mode = self._get_current_mode_code()
        if mode is None or mode == 0:
            msg = "Unsupported dishwasher mode"
            raise ValueError(msg)
        cast("MideaE1Device", self._device).start_work()

    def _get_current_mode_code(self) -> int | None:
        """Return raw code for the current dishwasher mode.

        Returns
        -------
        Raw mode code when the current mode is known.

        """
        mode_name = self._device.get_attribute("mode")
        modes = cast("MideaE1Device", self._device).modes
        for key, item in modes.items():
            if item == mode_name:
                return key
        return None

    @callback
    def update_state(self, status: Any) -> None:  # noqa: ANN401
        """Update entity state."""
        super().update_state(status)
        if (
            self.hass
            and not self.hass.is_stopping
            and ("mode" in status or self._power_attribute in status)
        ):
            self.schedule_update_ha_state()
