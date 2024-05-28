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
from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.ce import DeviceAttributes as CEAttributes
from midealocal.devices.x40 import DeviceAttributes as X40Attributes

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
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        if percentage:
            fan_speed = int(percentage / self.percentage_step + 0.5)
        else:
            fan_speed = None
        self._device.turn_on(fan_speed=fan_speed, mode=preset_mode)

    @property
    def preset_modes(self):
        return (
            self._device.preset_modes if hasattr(self._device, "preset_modes") else None
        )

    @property
    def is_on(self) -> bool:
        return self._device.get_attribute("power")

    @property
    def oscillating(self):
        return self._device.get_attribute("oscillate")

    @property
    def preset_mode(self):
        return self._device.get_attribute("mode")

    @property
    def fan_speed(self):
        return self._device.get_attribute("fan_speed")

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    def toggle(self):
        toggle = not self.is_on
        self._device.set_attribute(attr="power", value=toggle)

    def oscillate(self, oscillating: bool):
        self._device.set_attribute(attr="oscillate", value=oscillating)

    def set_preset_mode(self, preset_mode: str):
        self._device.set_attribute(attr="mode", value=preset_mode.capitalize())

    @property
    def percentage(self):
        return round(self.fan_speed * self.percentage_step)

    def set_percentage(self, percentage: int):
        fan_speed = round(percentage / self.percentage_step)
        self._device.set_attribute(attr="fan_speed", value=fan_speed)

    async def async_set_percentage(self, percentage: int):
        if percentage == 0:
            await self.async_turn_off()
        else:
            await self.hass.async_add_executor_job(self.set_percentage, percentage)

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


class MideaFAFan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count


class MideaB6Fan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count


class MideaACFreshAirFan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = 100

    @property
    def preset_modes(self):
        return self._device.fresh_air_fan_speeds

    @property
    def state(self):
        return (
            STATE_ON
            if self._device.get_attribute(ACAttributes.fresh_air_power)
            else STATE_OFF
        )

    @property
    def is_on(self) -> bool:
        return self.state == STATE_ON

    @property
    def fan_speed(self):
        return self._device.get_attribute(ACAttributes.fresh_air_fan_speed)

    def turn_on(self, percentage, preset_mode, **kwargs):
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=True)

    def turn_off(self):
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=False)

    def toggle(self):
        toggle = not self.is_on
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=toggle)

    def set_percentage(self, percentage: int):
        fan_speed = int(percentage / self.percentage_step + 0.5)
        self._device.set_attribute(
            attr=ACAttributes.fresh_air_fan_speed,
            value=fan_speed,
        )

    def set_preset_mode(self, preset_mode: str):
        self._device.set_attribute(attr=ACAttributes.fresh_air_mode, value=preset_mode)

    @property
    def preset_mode(self):
        return self._device.get_attribute(attr=ACAttributes.fresh_air_mode)


class MideaCEFan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count

    def turn_on(self, percentage, preset_mode, **kwargs):
        self._device.set_attribute(attr=CEAttributes.power, value=True)

    async def async_set_percentage(self, percentage: int):
        await self.hass.async_add_executor_job(self.set_percentage, percentage)


class Midea40Fan(MideaFan):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.OSCILLATE
        )
        self._attr_speed_count = 2

    @property
    def state(self):
        return (
            STATE_ON
            if self._device.get_attribute(attr=X40Attributes.fan_speed) > 0
            else STATE_OFF
        )

    def turn_on(self, percentage, preset_mode, **kwargs):
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=1)

    def turn_off(self):
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=0)
