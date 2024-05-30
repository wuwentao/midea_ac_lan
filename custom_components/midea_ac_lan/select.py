from typing import Any, cast
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    selects = []
    for entity_key, config in cast(
        dict, MIDEA_DEVICES[device.device_type]["entities"]
    ).items():
        if config["type"] == Platform.SELECT and entity_key in extra_switches:
            dev = MideaSelect(device, entity_key)
            selects.append(dev)
    async_add_entities(selects)


class MideaSelect(MideaEntity, SelectEntity):
    def __init__(self, device: Any, entity_key: str) -> None:
        super().__init__(device, entity_key)
        self._options_name = self._config.get("options")

    @property
    def options(self) -> list[str]:
        return cast(list, getattr(self._device, self._options_name))

    @property
    def current_option(self) -> str:
        return cast(str, self._device.get_attribute(self._entity_key))

    def select_option(self, option: str) -> None:
        self._device.set_attribute(self._entity_key, option)
