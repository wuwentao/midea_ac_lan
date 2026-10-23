"""Switch for Midea Lan."""

from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealan.device import DeviceType, MideaDevice
from midealan.devices.ed import DeviceAttributes as EDAttributes
from midealan.devices.ed import MideaEDDevice

from .const import DEVICES, DOMAIN, supports_device
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    switches = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] != Platform.SWITCH
            or not supports_device(device.model, device.subtype, config)
            or (not config.get("default") and entity_key not in extra_switches)
        ):
            continue
        required_attribute = config.get("required_attribute")
        if (
            required_attribute is not None
            and required_attribute not in device.attributes
        ):
            continue
        if device.device_type == DeviceType.ED and entity_key == "tea_bar":
            dev = MideaEDTeaBarBoilSwitch(device, entity_key)
        elif device.device_type == DeviceType.ED and entity_key == "tea_bar_child_lock":
            dev = MideaEDTeaBarChildLockSwitch(device, entity_key)
        else:
            dev = MideaSwitch(device, entity_key)
        switches.append(dev)
    async_add_entities(switches)


class MideaSwitch(MideaEntity, ToggleEntity):
    """Represent a Midea switch."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize a Midea switch."""
        super().__init__(device, entity_key)
        self._optimistic_value: bool | None = None

    @property
    def is_on(self) -> bool | None:
        """Whether the switch is on."""
        value = self._device.get_attribute(self._state_attribute_key)
        if value is None and self._config.get("optimistic"):
            return self._optimistic_value
        if "on_value" in self._config:
            return bool(value == self._config["on_value"])
        return cast("bool", value)

    @property
    def assumed_state(self) -> bool:
        """Whether the switch state is based on the last command."""
        return bool(self._config.get("optimistic"))

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn on switch."""
        self._device.set_attribute(
            attr=self._attribute_key,
            value=self._config.get("on_value", True),
        )
        if self._config.get("optimistic"):
            self._optimistic_value = True
            if self.hass:
                self.schedule_update_if_running()

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn off switch."""
        self._device.set_attribute(
            attr=self._attribute_key,
            value=self._config.get("off_value", False),
        )
        if self._config.get("optimistic"):
            self._optimistic_value = False
            if self.hass:
                self.schedule_update_if_running()


class MideaEDTeaBarBoilSwitch(MideaSwitch):
    """Accessible one-control switch for a subtype-395 tea bar."""

    _device: MideaEDDevice

    @property
    def is_on(self) -> bool:
        """Whether the automatic fill-and-boil cycle is active."""
        return bool(
            self._device.get_attribute(EDAttributes.boiling)
            or self._device.get_attribute(EDAttributes.dispensing),
        )

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Start the appliance's normal automatic fill-and-boil cycle."""
        self._device.set_attribute(EDAttributes.boiling, True)

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Stop the active boil cycle."""
        self._device.set_attribute(EDAttributes.boiling, False)


class MideaEDTeaBarChildLockSwitch(MideaSwitch):
    """Expose the tea-bar child lock with on/off switch semantics."""

    _device: MideaEDDevice

    @property
    def is_on(self) -> bool:
        """Whether the appliance child lock is enabled."""
        return bool(self._device.get_attribute(EDAttributes.child_lock))

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Enable the child lock using the official model command."""
        self._device.set_attribute(EDAttributes.child_lock, True)

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Disable the child lock using the official model command."""
        self._device.set_attribute(EDAttributes.child_lock, False)
