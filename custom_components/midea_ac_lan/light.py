"""Midea Light entries."""

import logging
from typing import Any, cast

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
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
        "dict",
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

    _device: Midea13Device

    # NOTE: supported_features / supported_color_modes / color_mode are computed
    # as properties (not latched in __init__). The device starts its socket
    # refresh on a background thread, so at construction time brightness,
    # color_temperature and rgb_color are all still None. Latching these in
    # __init__ would lock a dimmable/color-temp light to ONOFF forever, because
    # update_state never recomputes them. Recomputing per access reflects the
    # capabilities once the first status arrives.
    @property
    def supported_features(self) -> LightEntityFeature:
        """Midea Light supported features."""
        return _calc_supported_features(self._device)

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        """Midea Light supported color modes."""
        return _calc_supported_color_modes(self._device)

    @property
    def color_mode(self) -> ColorMode | str | None:
        """Midea Light current color mode."""
        # Call the concrete helper (returns set[ColorMode]) rather than the
        # supported_color_modes property, whose type is widened to
        # set[ColorMode] | set[str] | None to match LightEntity's base override.
        return self._calc_color_mode(_calc_supported_color_modes(self._device))

    def _calc_color_mode(self, supported: set[ColorMode]) -> ColorMode:
        """Midea Light calculate color mode.

        Returns
        -------
        Calculated color mode

        """
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
        return cast("bool", self._device.get_attribute(X13Attributes.power))

    @property
    def brightness(self) -> int | None:
        """Midea Light brightness."""
        return cast("int", self._device.get_attribute(X13Attributes.brightness))

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Midea Light rgb color."""
        return cast("tuple", self._device.get_attribute(X13Attributes.rgb_color))

    @property
    def color_temp(self) -> int | None:
        """Midea Light color temperature."""
        if not self.color_temp_kelvin:
            return None
        return round(1000000 / self.color_temp_kelvin)

    # https://developers.home-assistant.io/blog/2024/12/14/kelvin-preferred-color-temperature-unit
    @property
    def color_temp_kelvin(self) -> int | None:
        """Midea Light color temperature kelvin."""
        return cast("int", self._device.get_attribute(X13Attributes.color_temperature))

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
        return cast("list", self._device.effects)

    @property
    def effect(self) -> str | None:
        """Midea Light effect."""
        return cast("str", self._device.get_attribute(X13Attributes.effect))

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type]
        """Midea Light turn on."""
        if not self.is_on:
            self._device.set_attribute(attr=X13Attributes.power, value=True)
        for key, value in kwargs.items():
            if key == ATTR_BRIGHTNESS:
                self._device.set_attribute(attr=X13Attributes.brightness, value=value)
            if key == ATTR_COLOR_TEMP_KELVIN:
                self._device.set_attribute(
                    attr=X13Attributes.color_temperature,
                    value=value,
                )
            if key == ATTR_EFFECT:
                self._device.set_attribute(attr=X13Attributes.effect, value=value)

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Midea Light turn off."""
        self._device.set_attribute(attr=X13Attributes.power, value=False)

    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Midea Light update state."""
        if not self.hass:
            _LOGGER.warning(
                "Light update_state skipped for %s [%s]: HASS is None",
                self.name,
                type(self),
            )
            return
        self.schedule_update_if_running()
