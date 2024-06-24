"""Midea Fan entries."""

import logging
from typing import Any, cast

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.device import DeviceType
from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.ac import MideaACDevice
from midealocal.devices.b6 import MideaB6Device
from midealocal.devices.ce import DeviceAttributes as CEAttributes
from midealocal.devices.ce import MideaCEDevice
from midealocal.devices.fa import MideaFADevice
from midealocal.devices.x40 import DeviceAttributes as X40Attributes
from midealocal.devices.x40 import Midea40Device

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan entries."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs: list[
        MideaFAFan | MideaB6Fan | MideaACFreshAirFan | MideaCEFan | Midea40Fan
    ] = []
    for entity_key, config in cast(
        dict,
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] == Platform.FAN and (
            config.get("default") or entity_key in extra_switches
        ):
            if device.device_type == DeviceType.FA:
                devs.append(MideaFAFan(device, entity_key))
            elif device.device_type == DeviceType.B6:
                devs.append(MideaB6Fan(device, entity_key))
            elif device.device_type == DeviceType.AC:
                devs.append(MideaACFreshAirFan(device, entity_key))
            elif device.device_type == DeviceType.CE:
                devs.append(MideaCEFan(device, entity_key))
            elif device.device_type == DeviceType.X40:
                devs.append(Midea40Fan(device, entity_key))
    async_add_entities(devs)


class MideaFan(MideaEntity, FanEntity):
    """Midea Fan Entries Base Class."""

    @property
    def preset_modes(self) -> list[str] | None:
        """Midea Fan preset modes."""
        return (
            self._device.preset_modes if hasattr(self._device, "preset_modes") else None
        )

    @property
    def is_on(self) -> bool:
        """Midea Fan is on."""
        return cast(bool, self._device.get_attribute("power"))

    @property
    def oscillating(self) -> bool:
        """Midea Fan oscillating."""
        return cast(bool, self._device.get_attribute("oscillate"))

    @property
    def preset_mode(self) -> str | None:
        """Midea Fan preset mode."""
        return cast(str, self._device.get_attribute("mode"))

    @property
    def fan_speed(self) -> int | None:
        """Midea Fan fan speed."""
        return cast(int, self._device.get_attribute("fan_speed"))

    def turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """Midea Fan turn off."""
        self._device.set_attribute(attr="power", value=False)

    def oscillate(self, oscillating: bool) -> None:
        """Midea Fan oscillate."""
        self._device.set_attribute(attr="oscillate", value=oscillating)

    def set_preset_mode(self, preset_mode: str) -> None:
        """Midea Fan set preset mode."""
        self._device.set_attribute(attr="mode", value=preset_mode.capitalize())

    @property
    def percentage(self) -> int | None:
        """Midea Fan percentage."""
        if not self.fan_speed:
            return None
        return int(round(self.fan_speed * self.percentage_step))

    def set_percentage(self, percentage: int) -> None:
        """Midea Fan set percentage."""
        fan_speed = round(percentage / self.percentage_step)
        self._device.set_attribute(attr="fan_speed", value=fan_speed)

    async def async_set_percentage(self, percentage: int) -> None:
        """Midea Fan async set percentage."""
        if percentage == 0:
            await self.async_turn_off()
        else:
            await self.hass.async_add_executor_job(self.set_percentage, percentage)

    def update_state(self, status: Any) -> None:  # noqa: ANN401, ARG002
        """Midea Fan update state."""
        self.schedule_update_ha_state()


class MideaFAFan(MideaFan):
    """Midea FA Fan Entries."""

    _device: MideaFADevice

    def __init__(self, device: MideaFADevice, entity_key: str) -> None:
        """Midea FA Fan entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.OSCILLATE
            | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        """Midea FA Fan turn on."""
        fan_speed = int(percentage / self.percentage_step + 0.5) if percentage else None
        self._device.turn_on(fan_speed=fan_speed, mode=preset_mode)


class MideaB6Fan(MideaFan):
    """Midea B6 Fan Entries."""

    _device: MideaB6Device

    def __init__(self, device: MideaB6Device, entity_key: str) -> None:
        """Midea B6 Fan entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count

    def turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        """Midea B6 Fan turn on."""
        fan_speed = int(percentage / self.percentage_step + 0.5) if percentage else None
        self._device.turn_on(fan_speed=fan_speed, mode=preset_mode)


class MideaACFreshAirFan(MideaFan):
    """Midea AC Fresh Air Fan Entries."""

    _device: MideaACDevice

    def __init__(self, device: MideaACDevice, entity_key: str) -> None:
        """Midea AC Fresh Air Fan entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = 100

    @property
    def preset_modes(self) -> list[str] | None:
        """Midea AC Fan preset modes."""
        return cast(list, self._device.fresh_air_fan_speeds)

    @property
    def is_on(self) -> bool:
        """Midea AC Fan is on."""
        return cast(bool, self._device.get_attribute(ACAttributes.fresh_air_power))

    @property
    def fan_speed(self) -> int:
        """Midea AC Fan fan speed."""
        return cast(int, self._device.get_attribute(ACAttributes.fresh_air_fan_speed))

    def turn_on(
        self,
        percentage: int | None = None,  # noqa: ARG002
        preset_mode: str | None = None,  # noqa: ARG002
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        """Midea AC Fan tun on."""
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=True)

    def turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """Midea AC Fan turn off."""
        self._device.set_attribute(attr=ACAttributes.fresh_air_power, value=False)

    def set_percentage(self, percentage: int) -> None:
        """Midea AC Fan set percentage."""
        fan_speed = int(percentage / self.percentage_step + 0.5)
        self._device.set_attribute(
            attr=ACAttributes.fresh_air_fan_speed,
            value=fan_speed,
        )

    def set_preset_mode(self, preset_mode: str) -> None:
        """Midea AC Fan set preset mode."""
        self._device.set_attribute(attr=ACAttributes.fresh_air_mode, value=preset_mode)

    @property
    def preset_mode(self) -> str | None:
        """Midea AC Fan preset mode."""
        return cast(str, self._device.get_attribute(attr=ACAttributes.fresh_air_mode))


class MideaCEFan(MideaFan):
    """Midea CE Fan Entries."""

    _device: MideaCEDevice

    def __init__(self, device: MideaCEDevice, entity_key: str) -> None:
        """Midea CE Fan entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = self._device.speed_count

    def turn_on(
        self,
        percentage: int | None = None,  # noqa: ARG002
        preset_mode: str | None = None,  # noqa: ARG002
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        """Midea CE Fan turn on."""
        self._device.set_attribute(attr=CEAttributes.power, value=True)

    async def async_set_percentage(self, percentage: int) -> None:
        """Midea CE Fan async set percentage."""
        await self.hass.async_add_executor_job(self.set_percentage, percentage)


class Midea40Fan(MideaFan):
    """Midea X40 Fan Entries."""

    _device: Midea40Device

    def __init__(self, device: Midea40Device, entity_key: str) -> None:
        """Midea X40 Fan entity init."""
        super().__init__(device, entity_key)
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | FanEntityFeature.OSCILLATE
        )
        self._attr_speed_count = 2

    @property
    def is_on(self) -> bool:
        """Midea X40 Fan is on."""
        return cast(int, self._device.get_attribute(attr=X40Attributes.fan_speed)) > 0

    def turn_on(
        self,
        percentage: int | None = None,  # noqa: ARG002
        preset_mode: str | None = None,  # noqa: ARG002
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        """Midea X40 Fan turn on."""
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=1)

    def turn_off(self, **kwargs: Any) -> None:  # noqa: ANN401, ARG002
        """Midea X40 Fan turn off."""
        self._device.set_attribute(attr=X40Attributes.fan_speed, value=0)
