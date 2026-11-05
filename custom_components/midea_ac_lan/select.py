"""Select for Midea Lan."""

from typing import Any, cast

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealan.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_device
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up selects for device."""
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    selects = []
    for entity_key, config in cast(
        "dict",
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if (
            config["type"] != Platform.SELECT
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
        dev = MideaSelect(device, entity_key)
        if config.get("omit_when_no_options") and not dev.options:
            continue
        selects.append(dev)
    async_add_entities(selects)


class MideaSelect(MideaEntity, SelectEntity):
    """Represent a Midea select."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea select init."""
        super().__init__(device, entity_key)
        self._options_name = self._config.get("options")
        self._options_dict_name = self._config.get("options_dict")
        self._options_method = self._config.get("options_method")

    @property
    def options(self) -> list[str]:
        """Available options for the entity."""
        if self._options_method:
            return [
                str(option)
                for option in getattr(self._device, self._options_method)(
                    self._attribute_key,
                )
            ]
        if self._options_dict_name:
            options = self._get_options_dict()
            exclude = self._config.get("options_exclude_codes", [])
            return [name for code, name in options.items() if code not in exclude]
        if isinstance(self._options_name, dict):
            return list(self._options_name.values())
        if isinstance(self._options_name, list):
            return [str(option) for option in self._options_name]
        return cast("list", getattr(self._device, self._options_name))

    @property
    def current_option(self) -> str | None:
        """Currently selected option."""
        value = self._device.get_attribute(self._state_attribute_key)
        if value is None:
            return None
        if self._options_method:
            option = str(value)
            return option if option in self.options else None
        state_map = self._config.get("state_map")
        if state_map is not None:
            value = state_map.get(value)
        if isinstance(self._options_name, dict):
            return cast("str | None", self._options_name.get(value))
        option = (
            str(value) if isinstance(self._options_name, list) else cast("str", value)
        )
        return option if option in self.options else None

    @property
    def available(self) -> bool:
        """Whether the entity is available."""
        if not super().available:
            return False
        power_attribute = self._config.get("available_power_attribute")
        return not power_attribute or bool(self._device.get_attribute(power_attribute))

    def select_option(self, option: str) -> None:
        """Select entity option.

        Raises
        ------
        ValueError
            If a mapped option is not supported.

        """
        value: Any = option
        if isinstance(self._options_name, dict):
            value = self._get_dict_key_by_value(self._options_name, option)
            if value is None:
                raise ValueError(f"Unsupported select option: {option}")
        elif self._config.get("option_type") == "int":
            value = int(option)
        self._device.set_attribute(self._attribute_key, value)

    def _get_options_dict(self) -> dict[int, str]:
        """Return option dict from the backing midea-lan device.

        Returns
        -------
        Option labels keyed by the raw mode code.

        """
        return cast("dict[int, str]", getattr(self._device, self._options_dict_name))

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Update entity state."""
        super().update_state(status)
        power_attribute = self._config.get("available_power_attribute")
        if (
            power_attribute
            and self.hass
            and (self._attribute_key in status or power_attribute in status)
        ):
            self.schedule_update_if_running()

    @staticmethod
    def _get_dict_key_by_value(source: dict[int, str], value: str) -> int | None:
        for key, item in source.items():
            if item == value:
                return key
        return None
