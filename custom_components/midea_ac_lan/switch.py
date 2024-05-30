from typing import Any, cast
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.helpers.entity import ToggleEntity

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
    switches = []
    for entity_key, config in cast(
        dict, MIDEA_DEVICES[device.device_type]["entities"]
    ).items():
        if config["type"] == Platform.SWITCH and entity_key in extra_switches:
            dev = MideaSwitch(device, entity_key)
            switches.append(dev)
    async_add_entities(switches)


class MideaSwitch(MideaEntity, ToggleEntity):
    @property
    def is_on(self) -> bool:
        return cast(bool, self._device.get_attribute(self._entity_key))

    def turn_on(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr=self._entity_key, value=True)

    def turn_off(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr=self._entity_key, value=False)
