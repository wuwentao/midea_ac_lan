"""
fan.py
"""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_SWITCHES,
    STATE_OFF,
    STATE_ON,
    Platform,
)

from .const import DEVICES, DOMAIN
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.ce.device import DeviceAttributes as CEAttributes
from .midea.devices.x40.device import DeviceAttributes as X40Attributes
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    async_setup_entry
    """
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.FAN and (
            config.get("default") or entity_key in extra_switches
        ):
            if device.device_type == 0xFA:
                devs.append(MideaFAFan(device, entity_key))
            elif device.device_type == 0xB6:
                devs.append(MideaB6Fan(device, entity_key))
            elif device.device_type == 0xAC:
                devs.append(MideaACFreshAirFan(device, entity_key))
            elif device.device_type == 0xCE:
                devs.append(MideaCEFan(device, entity_key))
            elif device.device_type == 0x40:
                devs.append(Midea40Fan(device, entity_key))
    async_add_entities(devs)


class MideaFan(MideaEntity, FanEntity):
    """
    MideaFan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        turn_on
        """
        if percentage:
            fan_speed = int(percentage / self.percentage_step + 0.5)
        else:
            fan_speed = None
        self._device.turn_on(fan_speed=fan_speed, mode=preset_mode)

    @property
    def preset_modes(self):
        """
        preset_modes
        """
        return (
            self._device.preset_modes if hasattr(self._device, "preset_modes") else None
        )

    @property
    def is_on(self) -> bool:
        """
        is_on
        """
        return self._device.get_attribute("power")

    @property
    def oscillating(self):
        """
        oscillating
        """
        return self._device.get_attribute("oscillate")

    @property
    def preset_mode(self):
        """
        preset_mode
        """
        return self._device.get_attribute("mode")

    @property
    def fan_speed(self):
        """
        fan_speed
        """
        return self._device.get_attribute("fan_speed")

    def turn_off(self):
        """
        turn_off
        """
        self._device.set_attribute(attr="power", value=False)

    def toggle(self):
        """
        toggle
        """
        toggle = not self.is_on
        self._device.set_attribute(attr="power", value=toggle)

    def oscillate(self, oscillating: bool):
        """
        oscillate
        """
        self._device.set_attribute(attr="oscillate", value=oscillating)

    def set_preset_mode(self, preset_mode: str):
        """
        set_preset_mode
        """
        self._device.set_attribute(attr="mode", value=preset_mode.capitalize())

    @property
    def percentage(self):
        """
        percentage
        """
        return round(self.fan_speed * self.percentage_step)

    def set_percentage(self, percentage: int):
        """
        set_percentage
        """
        fan_speed = round(percentage / self.percentage_step)
        self._device.set_attribute(attr="fan_speed", value=fan_speed)

    async def async_set_percentage(self, percentage: int):
        """
        async_set_percentage
        """
        if percentage == 0:
            await self.async_turn_off()
        else:
            await self.hass.async_add_executor_job(self.set_percentage, percentage)

    def update_state(self, status):
        """
        update_state
        """
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(
                f"Entity {self.entity_id} update_state {repr(e)}, status = {status}"
            )


class MideaFAFan(MideaFan):
    """
    MideaFAFan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count


class MideaB6Fan(MideaFan):
    """
    MideaB6Fan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count


class MideaACFreshAirFan(MideaFan):
    """
    MideaACFreshAirFan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = 100

    @property
    def preset_modes(self):
        """
        preset_modes
        """
        return self._device.fresh_air_fan_speeds

    @property
    def state(self):
        """
        state
        """
        return (
            STATE_ON
            if self._device.get_attribute(ACAttributes.fresh_air_power)
            else STATE_OFF
        )

    @property
    def is_on(self) -> bool:
        """
        is_on
        """
        return self.state == STATE_ON

    @property
    def fan_speed(self):
        """
        fan_speed
        """
        return self._device.get_attribute(ACAttributes.fresh_air_fan_speed)

    def turn_on(self, percentage, preset_mode, **kwargs):
        """
        turn_on
        """
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=True)

    def turn_off(self):
        """
        turn_off
        """
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=False)

    def toggle(self):
        """
        toggle
        """
        toggle = not self.is_on
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=toggle)

    def set_percentage(self, percentage: int):
        """
        set_percentage
        """
        fan_speed = int(percentage / self.percentage_step + 0.5)
        self._device.set_attribute(
            attr=ACAttributes.fresh_air_fan_speed, value=fan_speed
        )

    def set_preset_mode(self, preset_mode: str):
        """
        set_preset_mode
        """
        self._device.set_attribute(attr=ACAttributes.fresh_air_mode, value=preset_mode)

    @property
    def preset_mode(self):
        """
        preset_mode
        """
        return self._device.get_attribute(attr=ACAttributes.fresh_air_mode)


class MideaCEFan(MideaFan):
    """
    MideaCEFan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count

    def turn_on(self, percentage, preset_mode, **kwargs):
        """
        turn_on
        """
        self._device.set_attribute(attr=CEAttributes.power, value=True)

    async def async_set_percentage(self, percentage: int):
        """
        async_set_percentage
        """
        await self.hass.async_add_executor_job(self.set_percentage, percentage)


class Midea40Fan(MideaFan):
    """
    Midea40Fan
    """

    def __init__(self, device, entity_key):
        """
        __init__
        """
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.OSCILLATE
        )
        self._attr_speed_count = 2

    @property
    def state(self):
        """
        state
        """
        return (
            STATE_ON
            if self._device.get_attribute(attr=X40Attributes.fan_speed) > 0
            else STATE_OFF
        )

    def turn_on(self, percentage, preset_mode, **kwargs):
        """
        turn_on
        """
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=1)

    def turn_off(self):
        """
        turn_off
        """
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=0)
