import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from midealocal.devices.x13 import DeviceAttributes as X13Attributes
from midealocal.devices.x13 import Midea13Device

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.LIGHT and (
            config.get("default") or entity_key in extra_switches
        ):
            devs.append(MideaLight(device, entity_key))
    async_add_entities(devs)


def _calc_supported_features(device: Midea13Device) -> LightEntityFeature:
    supported_features = LightEntityFeature(0)
    if device.get_attribute(X13Attributes.effect):
        supported_features |= LightEntityFeature.EFFECT
    return supported_features


def _calc_supported_color_modes(device: Midea13Device) -> set[ColorMode]:
    # https://github.com/home-assistant/core/blob/c34731185164aaf44419977c4086e9a7dd6c0a7f/homeassistant/components/light/__init__.py#L1278
    supported = set[ColorMode]()

    if device.get_attribute(X13Attributes.color_temperature) is not None:
        supported.add(ColorMode.COLOR_TEMP)
    if device.get_attribute(X13Attributes.rgb_color) is not None:
        supported.add(ColorMode.HS)
    if not supported and device.get_attribute(X13Attributes.brightness) is not None:
        supported = {ColorMode.BRIGHTNESS}

    if not supported:
        supported = {ColorMode.ONOFF}

    return supported


class MideaLight(MideaEntity, LightEntity):
    _attr_color_mode: ColorMode | str | None = None
    _attr_supported_color_modes: set[ColorMode] | set[str] | None = None
    _attr_supported_features: LightEntityFeature = LightEntityFeature(0)

    _device: Midea13Device

    def __init__(self, device: Midea13Device, entity_key: str):
        super().__init__(device, entity_key)
        self._attr_supported_features = _calc_supported_features(device)
        self._attr_supported_color_modes = _calc_supported_color_modes(device)
        self._attr_color_mode = self._calc_color_mode(self._attr_supported_color_modes)

    def _calc_color_mode(self, supported: set[ColorMode]) -> ColorMode:
        # https://github.com/home-assistant/core/blob/c34731185164aaf44419977c4086e9a7dd6c0a7f/homeassistant/components/light/__init__.py#L925
        if ColorMode.HS in supported and self.hs_color is not None:
            return ColorMode.HS
        if ColorMode.COLOR_TEMP in supported and self.color_temp_kelvin is not None:
            return ColorMode.COLOR_TEMP
        if ColorMode.BRIGHTNESS in supported and self.brightness is not None:
            return ColorMode.BRIGHTNESS
        if ColorMode.ONOFF in supported:
            return ColorMode.ONOFF
        return ColorMode.UNKNOWN

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
        return self._device.effects

    @property
    def effect(self):
        return self._device.get_attribute(X13Attributes.effect)

    def turn_on(self, **kwargs: Any):
        if not self.is_on:
            self._device.set_attribute(attr=X13Attributes.power, value=True)
        for key in kwargs:
            value = kwargs[key]
            if key == ATTR_BRIGHTNESS:
                self._device.set_attribute(attr=X13Attributes.brightness, value=value)
            if key == ATTR_COLOR_TEMP:
                self._device.set_attribute(
                    attr=X13Attributes.color_temperature,
                    value=round(1000000 / value),
                )
            if key == ATTR_EFFECT:
                self._device.set_attribute(attr=X13Attributes.effect, value=value)

    def turn_off(self):
        self._device.set_attribute(attr=X13Attributes.power, value=False)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(
                "Entity %s update_state %s, status = %s",
                self.entity_id,
                repr(e),
                status,
            )
