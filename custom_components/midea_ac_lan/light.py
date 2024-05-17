import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    LightEntity,
    LightEntityFeature,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    SUPPORT_EFFECT,
)
from homeassistant.const import (
    Platform,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
)
from .const import (
    DOMAIN,
    DEVICES
)
from .midea.devices.x13.device import DeviceAttributes as X13Attributes
from .midea_entity import MideaEntity
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.LIGHT and (config.get("default") or entity_key in extra_switches):
            devs.append(MideaLight(device, entity_key))
    async_add_entities(devs)


class MideaLight(MideaEntity, LightEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def is_on(self):
        return self._device.get_attribute(X13Attributes.power)

    @property
    def brightness(self):
        return self._device.get_attribute(X13Attributes.brightness)

    @property
    def rgb_color(self):
        return self._device.get_attribute(X13Attributes.rgb_color)

    @property
    def color_temp(self):
        return round(1000000 / self.color_temp_kelvin)

    @property
    def color_temp_kelvin(self):
        return self._device.get_attribute(X13Attributes.color_temperature)

    @property
    def min_mireds(self) -> int:
        return round(1000000 / self.max_color_temp_kelvin)

    @property
    def max_mireds(self) -> int:
        return round(1000000 / self.min_color_temp_kelvin)

    @property
    def min_color_temp_kelvin(self) -> int:
        return self._device.color_temp_range[0]

    @property
    def max_color_temp_kelvin(self) -> int:
        return self._device.color_temp_range[1]

    @property
    def effect_list(self):
        return getattr(self._device, "effects")

    @property
    def effect(self):
        return self._device.get_attribute(X13Attributes.effect)

    @property
    def supported_features(self) -> LightEntityFeature:
        supported_features = 0
        if self._device.get_attribute(X13Attributes.brightness):
            supported_features |= SUPPORT_BRIGHTNESS
        if self._device.get_attribute(X13Attributes.color_temperature):
            supported_features |= SUPPORT_COLOR_TEMP
        if self._device.get_attribute(X13Attributes.effect):
            supported_features |= SUPPORT_EFFECT
        if self._device.get_attribute(X13Attributes.rgb_color):
            supported_features |= SUPPORT_COLOR
        return supported_features

    def turn_on(self, **kwargs: Any):
        if not self.is_on:
            self._device.set_attribute(attr=X13Attributes.power, value=True)
        for key in kwargs:
            value = kwargs.get(key)
            if key == ATTR_BRIGHTNESS:
                self._device.set_attribute(attr=X13Attributes.brightness, value=value)
            if key == ATTR_COLOR_TEMP:
                self._device.set_attribute(attr=X13Attributes.color_temperature, value=round(1000000 / value))
            if key == ATTR_EFFECT:
                self._device.set_attribute(attr=X13Attributes.effect, value=value)

    def turn_off(self):
        self._device.set_attribute(attr=X13Attributes.power, value=False)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(f"Entity {self.entity_id} update_state {repr(e)}, status = {status}")
