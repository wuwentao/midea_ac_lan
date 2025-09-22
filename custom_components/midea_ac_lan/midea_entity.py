"""Base entity for Midea Lan."""

import logging
from typing import Any, cast

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import callback

if (MAJOR_VERSION, MINOR_VERSION) >= (2023, 9):
    from homeassistant.helpers.device_registry import DeviceInfo
else:
    from homeassistant.helpers.entity import (  # type: ignore[attr-defined]
        DeviceInfo,
    )
from homeassistant.helpers.entity import Entity
from midealocal.device import MideaDevice

from .const import DOMAIN
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


class MideaEntity(Entity):
    """Base Midea entity."""

    def __init__(self, device: MideaDevice, entity_key: str) -> None:
        """Initialize Midea base entity."""
        self._device = device
        self._device.register_update(self.update_state)
        self._config = cast(
            "dict",
            MIDEA_DEVICES[self._device.device_type]["entities"],
        )[entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._device_name = self._device.name

        # HA language setting:
        # 1. hass.config.language: Settings / System / General settings
        # 2. user language setting in user profile setting
        # Entity name translation based on hass.config.language
        # add language in /config/configuration.yaml will disable web UI setting
        # homeassistant:
        #    language: zh-Hans  # noqa: ERA001

        # Translating the name and attributes of entities:
        # https://developers.home-assistant.io/blog/2023/03/27/entity_name_translations/#translating-entity-name
        # https://developers.home-assistant.io/docs/internationalization/core
        # translation_key: if defined, Home Assistant will try to find a
        # translation in translations/<lang>.json.
        # If translation exists -> UI shows the translated string.
        # If translation not found -> fallback to "name" / device_class / entity_id.
        self._attr_translation_key = self._config.get("translation_key")

        # has_entity_name: MUST be True in modern HA (old False behavior is deprecated).
        self._attr_has_entity_name = True

        # Step 1: translation_key is defined
        # - If translation is found in the current language:
        #       -> UI displays the translated string.
        if self._attr_translation_key is not None:
            # skip set attr_name and use translation_key
            pass
            # set attr_name to None will only show device name without translaion_key
        # Step 2: No translation_key
        # but english "name" is explicitly set in config:
        #       -> UI displays this name directly (highest priority).
        elif self._config.get("name") is not None:
            self._attr_name = self._config["name"]
        # Step 3: No translation_key, no name,
        # fallback to device_class default label.
        # Example: device_class = temperature -> "Temperature".
        elif "device_class" in self._config:
            self._attr_name = None  # Let HA generate from device_class
        # Step 4: Nothing available,
        else:
            self._attr_name = (
                f"{self._device_name} {self._config.get('name')}"
                if "name" in self._config
                else f"{self._device_name}"
            )

    @property
    def device(self) -> MideaDevice:
        """Return device structure."""
        return self._device

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return {
            "manufacturer": "Midea",
            "model": f"{MIDEA_DEVICES[self._device.device_type]['name']} "
            f"{self._device.model}"
            f" ({self._device.subtype})",
            "identifiers": {(DOMAIN, str(self._device.device_id))},
            "name": self._device_name,
        }

    @property
    def unique_id(self) -> str:
        """Return entity unique id."""
        return self._unique_id

    @property
    def should_poll(self) -> bool:
        """Return true is integration should poll."""
        return False

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return bool(self._device.available)

    @property
    def icon(self) -> str:
        """Return entity icon."""
        return cast("str", self._config.get("icon"))

    @callback
    def update_state(self, status: Any) -> None:  # noqa: ANN401
        """Update entity state."""
        if not self.hass:
            _LOGGER.warning(
                "MideaEntity update_state for %s [%s] with status %s: HASS is None",
                self.name,
                type(self),
                status,
            )
            return

        if self.hass.is_stopping:
            _LOGGER.debug(
                "MideaEntity update_state for %s [%s] with status %s: HASS is stopping",
                self.name,
                type(self),
                status,
            )
            return

        if self._entity_key in status or "available" in status:
            self.schedule_update_ha_state()
