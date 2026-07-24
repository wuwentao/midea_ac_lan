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
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, format_mac
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
        self._config = cast(
            "dict",
            MIDEA_DEVICES[self._device.device_type]["entities"],
        )[entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        # Build entity_id with the correct platform domain (sensor.*, switch.*, …)
        # instead of the integration domain. Keeps the legacy "<device_id>_<key>"
        # object_id so existing entity_ids are unchanged, while fixing the HA
        # wrong-domain deprecation (breaks in HA 2027.5.0).
        ha_domain = self._config["type"]
        self.entity_id = f"{ha_domain}.{self._device.device_id}_{entity_key}"
        self._device_name = self._device.name

        # HA language setting:
        # 1. hass.config.language: Settings / System / General settings
        # 2. user language setting in user profile setting
        # Entity name translation based on hass.config.language
        # add language in /config/configuration.yaml will disable web UI setting
        # homeassistant:
        #    language: zh-Hans  # ruff:ignore[commented-out-code]

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
        """Underlying Midea device instance."""
        return self._device

    @property
    def device_info(self) -> DeviceInfo:
        """Device registry info for the entity."""
        info: DeviceInfo = {
            "manufacturer": "Midea",
            "model": f"{MIDEA_DEVICES[self._device.device_type]['name']} "
            f"{self._device.model}"
            f" ({self._device.subtype})",
            "identifiers": {(DOMAIN, str(self._device.device_id))},
            "name": self._device_name,
        }
        if self._device.mac:
            info["connections"] = {
                (CONNECTION_NETWORK_MAC, format_mac(self._device.mac)),
            }
        if self._device.serial_number:
            info["serial_number"] = self._device.serial_number
        return info

    @property
    def unique_id(self) -> str:
        """Unique id of the entity."""
        return self._unique_id

    @property
    def should_poll(self) -> bool:
        """Whether the integration should poll for updates."""
        return False

    @property
    def available(self) -> bool:
        """Whether the entity is available."""
        return bool(self._device.available)

    @property
    def icon(self) -> str:
        """Icon for the entity."""
        return cast("str", self._config.get("icon"))

    async def async_added_to_hass(self) -> None:
        """Subscribe to device updates once the entity is added to HA.

        Registering the callback here (rather than in ``__init__``) ensures an
        entity that is constructed but never added to HA never receives updates,
        which avoids the recurring "HASS is None" warnings.
        """
        await super().async_added_to_hass()
        self._device.register_update(self.update_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from device updates when the entity is removed from HA."""
        await super().async_will_remove_from_hass()
        self._device.unregister_update(self.update_state)

    @callback
    def schedule_update_if_running(self) -> None:
        """Schedule a state write unless HA is shutting down.

        Shared by the base ``update_state`` and by the per-device-type
        subclasses that override it (climate, fan, light, water_heater,
        humidifier), so the shutdown guard lives in exactly one place and the
        main control entities are protected too (issues #798 and #809).

        The caller is responsible for the ``self.hass is None`` guard.

        Raises:
            RuntimeError: If ``schedule_update_ha_state()`` fails for a reason
                other than the event loop being closed during shutdown.

        """
        if self.hass.is_stopping:
            _LOGGER.debug(
                "MideaEntity update_state for %s [%s]: HASS is stopping",
                self.name,
                type(self),
            )
            return

        # A device background thread can still deliver an update after the HA
        # event loop has been closed during shutdown. Scheduling a state write
        # then raises RuntimeError because the loop is already closed (issues
        # #798 and #809). The is_stopping guard above covers the common case,
        # but a race remains between that check and the schedule call, so also
        # guard against the closed loop and swallow the residual RuntimeError.
        if self.hass.loop.is_closed():
            return
        try:
            self.schedule_update_ha_state()
        except RuntimeError:
            # Only swallow the shutdown race; re-raise any unrelated RuntimeError.
            if not self.hass.loop.is_closed():
                raise
            _LOGGER.debug(
                "Ignoring update for %s: event loop closed during shutdown",
                self.name,
            )

    @callback
    def update_state(self, status: Any) -> None:  # ruff:ignore[any-type]
        """Update entity state."""
        if not self.hass:
            # Defensive guard for the is_stopping access below. Since the update
            # callback is now registered in async_added_to_hass (#869), hass is
            # always set on the normal path, so this is debug (like is_stopping).
            _LOGGER.debug(
                "MideaEntity update_state for %s [%s] with status %s: HASS is None",
                self.name,
                type(self),
                status,
            )
            return

        if self._entity_key not in status and "available" not in status:
            return

        self.schedule_update_if_running()
