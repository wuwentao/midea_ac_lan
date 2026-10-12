"""Switch for Midea Lan."""

from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealan.device import DeviceType
from midealan.devices.ed import DeviceAttributes as EDAttributes
from midealan.devices.ed import MideaEDDevice

from .const import DEVICES, DOMAIN, supports_device
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

# 0x9C controls whose library setter expects "on"/"off" strings, not booleans.
X9C_ON_OFF_SWITCHES = ("total_power", "ai_voice_microphone")
X9C_STATE_ON = "on"
X9C_STATE_OFF = "off"


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
        elif device.device_type == DeviceType.X9C and entity_key in X9C_ON_OFF_SWITCHES:
            dev = MideaX9COnOffSwitch(device, entity_key)
        else:
            dev = MideaSwitch(device, entity_key)
        switches.append(dev)
    async_add_entities(switches)


class MideaSwitch(MideaEntity, ToggleEntity):
    """Represent a Midea switch."""

    @property
    def is_on(self) -> bool:
        """Whether the switch is on."""
        return cast("bool", self._device.get_attribute(self._entity_key))

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn on switch."""
        self._device.set_attribute(attr=self._entity_key, value=True)

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn off switch."""
        self._device.set_attribute(attr=self._entity_key, value=False)


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


class MideaX9COnOffSwitch(MideaSwitch):
    """Switch for 0x9C controls that expect "on"/"off" strings, not booleans.

    The 0x9C library rejects a bare ``bool`` for ``total_power`` and
    ``ai_voice_microphone`` (they map to protocol enums), so translate the
    Home Assistant toggle into the string values the device expects, and read
    the string state back as a boolean.
    """

    @property
    def is_on(self) -> bool:
        """Whether the control reports the "on" state."""
        return bool(self._device.get_attribute(self._entity_key) == X9C_STATE_ON)

    def turn_on(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn on the control using its string on value."""
        self._device.set_attribute(attr=self._entity_key, value=X9C_STATE_ON)

    def turn_off(self, **kwargs: Any) -> None:  # ruff:ignore[any-type, unused-method-argument]
        """Turn off the control using its string off value."""
        self._device.set_attribute(attr=self._entity_key, value=X9C_STATE_OFF)
