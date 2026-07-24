"""Select for Midea Lan."""

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.device import MideaDevice

from .const import DEVICES, DOMAIN, supports_model
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

if TYPE_CHECKING:
    from midealocal.devices.e1 import MideaE1Device


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
            or not supports_model(device.model, config)
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
        selects.append(dev)
    async_add_entities(selects)


class MideaSelect(MideaEntity, SelectEntity):
    """Represent a Midea select."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Midea select init."""
        super().__init__(device, entity_key)
        self._attribute_key = self._config.get("attribute", entity_key)
        self._options_name = self._config.get("options")
        self._options_dict_name = self._config.get("options_dict")

    @property
    def options(self) -> list[str]:
        """Return entity options."""
        if self._options_dict_name:
            options = self._get_options_dict()
            codes_by_model = self._config.get("options_codes_by_model", {})
            codes = codes_by_model.get(str(self._device.model)) or self._config.get(
                "options_codes",
            )
            if codes:
                return [options[code] for code in codes if code in options]
            return list(options.values())
        return cast("list", getattr(self._device, self._options_name))

    @property
    def current_option(self) -> str | None:
        """Return entity current option."""
        option = cast("str | None", self._device.get_attribute(self._attribute_key))
        return option if option in self.options else None

    @property
    def available(self) -> bool:
        """Return entity availability."""
        if not super().available:
            return False
        power_attribute = self._config.get("available_power_attribute")
        return not power_attribute or bool(self._device.get_attribute(power_attribute))

    def select_option(self, option: str) -> None:
        """Select entity option."""
        if self._config.get("set_message") == "e1_work_mode":
            self._select_e1_work_mode(option)
            return
        self._device.set_attribute(self._attribute_key, option)

    def _get_options_dict(self) -> dict[int, str]:
        """Return option dict from the backing midea-local device.

        Returns
        -------
        Option labels keyed by the raw mode code.

        """
        return cast("dict[int, str]", getattr(self._device, self._options_dict_name))

    def _select_e1_work_mode(self, option: str) -> None:
        """Set dishwasher work mode via midea-local's public E1 API.

        Raises
        ------
        ValueError
            If the requested option is not a supported work mode.

        """
        mode = self._get_dict_key_by_value(self._get_options_dict(), option)
        if mode is None:
            raise ValueError(f"Unsupported dishwasher mode: {option}")
        cast("MideaE1Device", self._device).set_work_mode(mode)

    @callback
    def update_state(self, status: Any) -> None:  # noqa: ANN401
        """Update entity state."""
        super().update_state(status)
        power_attribute = self._config.get("available_power_attribute")
        if (
            power_attribute
            and self.hass
            and not self.hass.is_stopping
            and (self._attribute_key in status or power_attribute in status)
        ):
            self.schedule_update_ha_state()

    @staticmethod
    def _get_dict_key_by_value(source: dict[int, str], value: str) -> int | None:
        for key, item in source.items():
            if item == value:
                return key
        return None
