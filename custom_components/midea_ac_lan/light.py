"""Midea Light entries."""

import logging
from typing import Any, cast

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.devices.x13 import DeviceAttributes as X13Attributes
from midealocal.devices.x13 import Midea13Device

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up light entries."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs = []
    for entity_key, config in cast(
        dict,
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
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
    """Midea Light Entries."""

    _attr_color_mode: ColorMode | str | None = None
    _attr_supported_color_modes: set[ColorMode] | set[str] | None = None
    _attr_supported_features: LightEntityFeature = LightEntityFeature(0)

    _device: Midea13Device

    def __init__(self, device: Midea13Device, entity_key: str) -> None:
        """Midea Light entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = _calc_supported_features(device)
        self._attr_supported_color_modes = _calc_supported_color_modes(device)
        self._attr_color_mode = self._calc_color_mode(self._attr_supported_color_modes)

    def _calc_color_mode(self, supported: set[ColorMode]) -> ColorMode:
        """Midea Light calculate color mode."""
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
    def is_on(self) -> bool:
        """Midea Light is on."""
        return cast(bool, self._device.get_attribute(X13Attributes.power))

    @property
    def brightness(self) -> int | None:
        """Midea Light brightness."""
        return cast(int, self._device.get_attribute(X13Attributes.brightness))

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Midea Light rgb color."""
        return cast(tuple, self._device.get_attribute(X13Attributes.rgb_color))

    @property
    def color_temp(self) -> int | None:
        """Midea Light color temperature."""
        if not self.color_temp_kelvin:
            return None
        return round(1000000 / self.color_temp_kelvin)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Midea Light color temperature kelvin."""
        return cast(int, self._device.get_attribute(X13Attributes.color_temperature))

    @property
    def min_mireds(self) -> int:
        """Midea Light color temperature min mireds."""
        return round(1000000 / self.max_color_temp_kelvin)

    @property
    def max_mireds(self) -> int:
        """Midea Light color temperature max mireds."""
        return round(1000000 / self.min_color_temp_kelvin)

    @property
    def min_color_temp_kelvin(self) -> int:
        """Midea Light min color temperature kelvin."""
        return self._device.color_temp_range[0]

    @property
    def max_color_temp_kelvin(self) -> int:
        """Midea Light max color temperature kelvin."""
        return self._device.color_temp_range[1]

    @property
    def effect_list(self) -> list[str] | None:
        """Midea Light effect list."""
        return cast(list, self._device.effects)

    @property
    def effect(self) -> str | None:
        """Midea Light effect."""
        return cast(str, self._device.get_attribute(X13Attributes.effect))

    def turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Midea Light turn on."""
        if not self.is_on:
            self._device.set_attribute(attr=X13Attributes.power, value=True)
        for key, value in kwargs.items():
            if key == ATTR_BRIGHTNESS:
                self._device.set_attribute(attr=X13Attributes.brightness, value=value)
            if key == ATTR_COLOR_TEMP:
                self._device.set_attribute(
                    attr=X13Attributes.color_temperature,
                    value=round(1000000 / value),
                )
            if key == ATTR_EFFECT:
                self._device.set_attribute(attr=X13Attributes.effect, value=value)

    def turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """Midea Light turn off."""
        self._device.set_attribute(attr=X13Attributes.power, value=False)

    def update_state(self, status: Any) -> None:  # noqa: ANN401,ARG002
        """Midea Light update state."""
        self.schedule_update_ha_state()
