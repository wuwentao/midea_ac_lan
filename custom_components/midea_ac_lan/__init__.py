"""Init for Midea LAN.

integration load process:
1. component setup: `async_setup`
    1.1 use `hass.services.async_register` to register service
2. config entry setup: `async_setup_entry`
    2.1 forward the Config Entry to the platform `async_forward_entry_setups`
    2.2 register listener `update_listener`
3. unloading a config entry: `async_unload_entry`
"""

import asyncio
import logging
from typing import Any, cast

import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SWITCHES,
    CONF_TOKEN,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.typing import ConfigType
from midealan.device import DeviceType, MideaDevice, ProtocolVersion
from midealan.devices import device_selector
from midealan.discover import discover

from .const import (
    ALL_PLATFORM,
    CONF_ACCOUNT,
    CONF_CLOUD_NAME,
    CONF_KEY,
    CONF_MAC,
    CONF_MANUFACTURER_CODE,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL,
    CONF_SN,
    CONF_SN8,
    CONF_SUBTYPE,
    DEVICES,
    DOMAIN,
    EXTRA_SWITCH,
    supports_device,
)
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)

_ATTRIBUTE_ALIASES: dict[int, dict[str, str]] = {
    DeviceType.E7: {"function_no": "function_num"},
    DeviceType.EB: {"function_no": "function_num"},
}


def _close_device(device: MideaDevice) -> None:
    """Close a Midea device connection without failing unload/setup cleanup."""
    try:
        device.close()
    except (OSError, ConnectionError, AttributeError) as e:
        _LOGGER.warning("Failed to close Midea socket cleanly: %s", e)


def _device_store(hass: HomeAssistant) -> dict[int, MideaDevice]:
    """Return the integration's loaded device map.

    Returns
    -------
    Device id to Midea device mapping.

    """
    return cast(
        "dict[int, MideaDevice]",
        hass.data.setdefault(DOMAIN, {}).setdefault(DEVICES, {}),
    )


def _remove_unsupported_entities(
    hass: HomeAssistant,
    device: MideaDevice,
) -> None:
    """Remove stale entities that do not apply to this model and subtype."""
    registry = er.async_get(hass)
    entities = cast(
        "dict[str, dict[str, Any]]",
        MIDEA_DEVICES[device.device_type]["entities"],
    )
    for entity_key, config in entities.items():
        if supports_device(device.model, device.subtype, config):
            continue
        unique_id = f"{DOMAIN}.{device.device_id}_{entity_key}"
        entity_domain = cast("str", config["type"].value)
        entity_id = registry.async_get_entity_id(
            entity_domain,
            DOMAIN,
            unique_id,
        )
        if entity_id is None:
            legacy_entity_id = f"{entity_domain}.{device.device_id}_{entity_key}"
            if registry.async_get(legacy_entity_id) is not None:
                entity_id = legacy_entity_id
        if entity_id is not None:
            registry.async_remove(entity_id)


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Option flow signal update.

    Registered in `async_setup_entry` via
    `config_entry.async_on_unload(config_entry.add_update_listener(...))`, so it
    is attached when the entry loads and detached at unload. Reload the entry so
    the changed options (customize JSON, IP override, refresh interval, and the
    extra sensor/switch selection) are re-applied through the normal setup path.

    Reloading avoids the previous fire-and-forget re-setup, which awaited the
    platform unload but then re-forwarded setup via an untracked
    `async_create_task` — swallowing any setup error and racing the customize/
    ip/refresh application that followed.
    """
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:  # ruff:ignore[unused-function-argument]
    """Set up midea_lan component when load this integration.

    Returns
    -------
    True if entry is configured.

    """
    hass.data.setdefault(DOMAIN, {})
    attributes = []
    for device_entities in MIDEA_DEVICES.values():
        for attribute_name, attribute in cast(
            "dict",
            device_entities["entities"],
        ).items():
            attribute_key = (
                attribute_name
                if isinstance(attribute_name, str)
                else attribute_name.value
            )
            if (
                attribute.get("type") in EXTRA_SWITCH
                and attribute_key not in attributes
            ):
                attributes.append(attribute_key)
    for aliases in _ATTRIBUTE_ALIASES.values():
        for legacy_attribute in aliases:
            if legacy_attribute not in attributes:
                attributes.append(legacy_attribute)

    def service_set_attribute(service: Any) -> None:  # ruff:ignore[any-type]
        """Set service attribute func."""
        device_id: int = service.data["device_id"]
        requested_attr = service.data["attribute"]
        value = service.data["value"]
        dev: MideaDevice = hass.data[DOMAIN][DEVICES].get(device_id)
        if dev:
            attr = _ATTRIBUTE_ALIASES.get(dev.device_type, {}).get(
                requested_attr,
                requested_attr,
            )
            if attr == "fan_speed" and value == "auto":
                value = 102
            item = None
            if dev_ := MIDEA_DEVICES.get(dev.device_type):
                item = cast("dict", dev_["entities"]).get(attr)
            if item is not None and item.get("type") in EXTRA_SWITCH:
                dev.set_attribute(attr=item.get("attribute", attr), value=value)
            elif (
                dev.device_type == DeviceType.AC
                and attr == "fan_speed"
                and value in range(103)
            ):
                dev.set_attribute(attr=attr, value=value)
            else:
                _LOGGER.error(
                    "Appliance [%s] has no attribute %s or value is invalid",
                    device_id,
                    requested_attr,
                )

    def service_send_command(service: Any) -> None:  # ruff:ignore[any-type]
        """Send command to service func."""
        device_id = service.data.get("device_id")
        cmd_type = service.data.get("cmd_type")
        cmd_body = service.data.get("cmd_body")
        try:
            cmd_body = bytearray.fromhex(cmd_body)
        except ValueError:
            _LOGGER.exception(
                "Appliance [%s] invalid cmd_body, a hexadecimal string required",
                device_id,
            )
            return
        dev = hass.data[DOMAIN][DEVICES].get(device_id)
        if dev:
            dev.send_command(cmd_type, cmd_body)

    # register service func calls:
    # `service_set_attribute`, service.yaml key: `set_attribute`
    hass.services.async_register(
        DOMAIN,
        "set_attribute",
        service_set_attribute,
        schema=vol.Schema(
            {
                vol.Required("device_id"): vol.Coerce(int),
                vol.Required("attribute"): vol.In(attributes),
                vol.Required("value"): vol.Any(int, cv.boolean, str),
            },
        ),
    )

    # register service func calls:
    # `service_send_command`, service.yaml key: `send_command`
    hass.services.async_register(
        DOMAIN,
        "send_command",
        service_send_command,
        schema=vol.Schema(
            {
                vol.Required("device_id"): vol.Coerce(int),
                vol.Required("cmd_type"): vol.In([2, 3]),
                vol.Required("cmd_body"): str,
            },
        ),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:  # ruff: ignore[too-many-locals]
    """Set up platform for current integration.

    Returns
    -------
    True if entry is configured.

    Raises
    ------
    CancelledError
        If setup is cancelled (e.g. Home Assistant stops), after closing the device.

    """
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        return True
    name = config_entry.data.get(CONF_NAME)
    device_id: int = config_entry.data[CONF_DEVICE_ID]
    if name is None:
        name = f"{device_id}"
    if device_type is None:
        device_type = 0xAC
    token: str = config_entry.data.get(CONF_TOKEN) or ""
    key: str = config_entry.data.get(CONF_KEY) or ""
    ip_address = config_entry.options.get(CONF_IP_ADDRESS, None)
    if ip_address is None:
        ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    refresh_interval = config_entry.options.get(CONF_REFRESH_INTERVAL)
    port: int = config_entry.data[CONF_PORT]
    model: str = config_entry.data[CONF_MODEL]
    subtype = config_entry.data.get(CONF_SUBTYPE, 0)
    protocol: ProtocolVersion = ProtocolVersion(config_entry.data[CONF_PROTOCOL])
    customize: str = config_entry.options.get(CONF_CUSTOMIZE, "")
    mac: str | None = config_entry.data.get(CONF_MAC)
    serial_number: str | None = config_entry.data.get(CONF_SN)
    # Cloud-derived identity fields (sn8/manufacturer_code/cloud_name) are read
    # inline at the device_selector call below to keep the local-variable count
    # within the lint limit.
    if protocol == ProtocolVersion.V3 and (key == "" or token == ""):
        _LOGGER.error("For V3 devices, the key and the token is required")
        return False
    # device_selector in `midealan/devices/__init__.py`
    device = await hass.async_add_import_executor_job(
        device_selector,
        name,
        device_id,
        device_type,
        ip_address,
        port,
        token,
        key,
        protocol,
        model,
        subtype,
        customize,
        mac,
        serial_number,
        config_entry.data.get(CONF_SN8),
        config_entry.data.get(CONF_MANUFACTURER_CODE),
        config_entry.data.get(CONF_CLOUD_NAME),
    )
    if device:
        if refresh_interval is not None:
            device.set_refresh_interval(refresh_interval)
        device.open()
        _device_store(hass)[device_id] = device

        async def _async_close_on_stop(_event: Event) -> None:
            """Stop the device thread so it can't hold up Home Assistant's exit."""
            # close() waits for the socket lock, which connect() holds for the
            # whole connection attempt, so keep it off the event loop.
            await hass.async_add_executor_job(_close_device, device)

        # Home Assistant does not unload config entries on shutdown, so without
        # this the non-daemon device thread keeps running (e.g. sleeping up to
        # 600 s between reconnect attempts) and delays the process exit.
        # Registered before the platform forward so a stop during setup is covered.
        remove_stop_listener = hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP,
            _async_close_on_stop,
        )
        try:
            _remove_unsupported_entities(hass, device)
            # Forward the setup of an entry to all platforms
            await hass.config_entries.async_forward_entry_setups(
                config_entry,
                ALL_PLATFORM,
            )
        except (Exception, asyncio.CancelledError):
            # On supported HA versions a forwarding failure or cancellation
            # bypasses `async_on_unload`, so detach the listener explicitly to
            # avoid leaking it (and the closed device) on the EventBus.
            remove_stop_listener()
            _device_store(hass).pop(device_id, None)
            await hass.async_add_executor_job(_close_device, device)
            raise
        # Keep the stop listener until the entry is unloaded or reloaded.
        config_entry.async_on_unload(remove_stop_listener)
        # Listener `update_listener` is
        # attached when the entry is loaded
        # and detached when it's unloaded
        config_entry.async_on_unload(config_entry.add_update_listener(update_listener))

        return True
    return False


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Clean up entities, unsubscribe event listener and close all connections.

    Returns
    -------
    True if entry is unloaded.

    """
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        return True
    # Unload the platforms first; only tear the device down if that succeeded,
    # and report the real result so a failed platform unload isn't masked.
    # bool() keeps mypy happy: async_unload_platforms is typed to return Any.
    unload_ok = bool(
        await hass.config_entries.async_unload_platforms(
            config_entry,
            ALL_PLATFORM,
        ),
    )
    if unload_ok:
        device_id = config_entry.data.get(CONF_DEVICE_ID)
        if device_id is not None:
            dm = _device_store(hass).pop(device_id, None)
            if dm is not None:
                _close_device(dm)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry.

    Returns
    -------
    True if entry is migrated.

    """
    # 1 -> 2:  convert device identifiers from int to str
    if config_entry.version == 1:
        _LOGGER.debug("Migrating configuration from version 1")

        hass.config_entries.async_update_entry(config_entry, version=2)

        # Migrate device.
        await _async_migrate_device_identifiers(hass, config_entry)

        _LOGGER.debug("Migration to configuration version 2 successful")

    # 2.1 -> 2.2: backfill mac address and serial number for existing devices
    entry_version_2 = 2
    migration_minor_version = config_entry.minor_version
    if config_entry.version == entry_version_2 and config_entry.minor_version == 1:
        _LOGGER.debug("Migrating configuration from version 2.1")

        if await _async_backfill_mac_and_sn(hass, config_entry):
            hass.config_entries.async_update_entry(config_entry, minor_version=2)
            migration_minor_version = 2

            _LOGGER.debug("Migration to configuration version 2.2 successful")
        else:
            _LOGGER.debug(
                "Device %s did not respond to discovery;"
                " mac/serial number migration will be retried on next start",
                config_entry.data.get(CONF_DEVICE_ID),
            )
            # The attribute rename is independent and idempotent. Apply it now,
            # but retain 2.1 so identity discovery is retried next startup.
            _migrate_function_num(hass, config_entry, advance_version=False)
            return True

    # 2.2 -> 2.3: rename the EB function number attribute without losing an
    # optional selection or orphaning its existing entity registry entry.
    entry_minor_version_2 = 2
    if (
        config_entry.version == entry_version_2
        and migration_minor_version == entry_minor_version_2
    ):
        _migrate_function_num(hass, config_entry, advance_version=True)

    return True


def _migrate_function_num(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    *,
    advance_version: bool,
) -> None:
    """Migrate the released E7/EB function_no selection and entity identity."""
    legacy_attribute = "function_no"
    current_attribute = "function_num"
    options = dict(config_entry.options)

    if config_entry.data.get(CONF_TYPE) in _ATTRIBUTE_ALIASES:
        selected_controls = options.get(CONF_SWITCHES)
        if (
            isinstance(selected_controls, list)
            and legacy_attribute in selected_controls
        ):
            options[CONF_SWITCHES] = [
                current_attribute if item == legacy_attribute else item
                for item in selected_controls
            ]

        device_id = config_entry.data.get(CONF_DEVICE_ID)
        if device_id is not None:
            registry = er.async_get(hass)
            legacy_unique_id = f"{DOMAIN}.{device_id}_{legacy_attribute}"
            entity_id = registry.async_get_entity_id(
                Platform.NUMBER,
                DOMAIN,
                legacy_unique_id,
            )
            if entity_id is None:
                legacy_entity_id = f"{Platform.NUMBER}.{device_id}_{legacy_attribute}"
                legacy_entry = registry.async_get(legacy_entity_id)
                if (
                    legacy_entry is not None
                    and legacy_entry.domain == Platform.NUMBER
                    and legacy_entry.platform == DOMAIN
                    and legacy_entry.config_entry_id == config_entry.entry_id
                    and legacy_entry.unique_id == legacy_unique_id
                ):
                    entity_id = legacy_entity_id
            if entity_id is not None:
                registry.async_update_entity(
                    entity_id,
                    new_unique_id=f"{DOMAIN}.{device_id}_{current_attribute}",
                )

    update: dict[str, Any] = {}
    if options != config_entry.options:
        update["options"] = options
    if advance_version:
        update["minor_version"] = 3
    if update:
        hass.config_entries.async_update_entry(config_entry, **update)


async def _async_backfill_mac_and_sn(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> bool:
    """Best-effort discovery to backfill mac address and serial number.

    Returns
    -------
    True if the entry already had the data, has no IP/device id to look up,
    or was successfully updated. False if the device did not answer
    discovery and the migration should be retried on a later start.

    """
    if config_entry.data.get(CONF_TYPE) == CONF_ACCOUNT:
        return True
    if config_entry.data.get(CONF_MAC) or config_entry.data.get(CONF_SN):
        return True
    # Honor an IP override set via the options flow (e.g. after a DHCP change),
    # mirroring async_setup_entry; the data IP may be stale.
    ip_address = config_entry.options.get(CONF_IP_ADDRESS)
    if ip_address is None:
        ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if ip_address is None or device_id is None:
        return True
    try:
        found_devices = await hass.async_add_executor_job(
            lambda: discover(ip_address=ip_address),
        )
    except Exception:
        # Best-effort migration: any discovery failure (socket error, malformed
        # reply from a legacy device, parse error) must not break entry setup.
        # Retry on the next start instead.
        _LOGGER.debug(
            "Discovery for device %s failed; mac/serial number migration"
            " will be retried on next start",
            device_id,
            exc_info=True,
        )
        return False
    device = found_devices.get(int(device_id))
    if device is None:
        return False
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_MAC: device.get(CONF_MAC),
            CONF_SN: device.get(CONF_SN),
        },
    )
    return True


async def _async_migrate_device_identifiers(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
) -> None:
    """Migrate the device identifiers to the new format."""
    device_registry = dr.async_get(hass)
    device_entry_found = False
    for device_entry in dr.async_entries_for_config_entry(
        device_registry,
        config_entry.entry_id,
    ):
        for identifier in device_entry.identifiers:
            # Device found in registry. Update identifiers.
            new_identifiers = {
                (
                    DOMAIN,
                    str(identifier[1]),
                ),
            }
            _LOGGER.debug(
                "Migrating device identifiers from %s to %s",
                device_entry.identifiers,
                new_identifiers,
            )
            device_registry.async_update_device(
                device_id=device_entry.id,
                new_identifiers=new_identifiers,
            )
            # Device entry found. Leave inner for loop.
            device_entry_found = True
            break

        # Leave outer for loop if device entry is already found.
        if device_entry_found:
            break
