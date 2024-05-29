import logging
from typing import Any, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_CUSTOMIZE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_TOKEN,
    CONF_TYPE,
    MAJOR_VERSION,
    MINOR_VERSION,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from midealocal.devices import device_selector

from .const import (
    ALL_PLATFORM,
    CONF_ACCOUNT,
    CONF_KEY,
    CONF_MODEL,
    CONF_REFRESH_INTERVAL,
    CONF_SUBTYPE,
    DEVICES,
    DOMAIN,
    EXTRA_SWITCH,
)
from .midea_devices import MIDEA_DEVICES

_LOGGER = logging.getLogger(__name__)


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    for platform in ALL_PLATFORM:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    for platform in ALL_PLATFORM:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform),
        )
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    customize = config_entry.options.get(CONF_CUSTOMIZE, "")
    ip_address = config_entry.options.get(CONF_IP_ADDRESS, None)
    refresh_interval = config_entry.options.get(CONF_REFRESH_INTERVAL, None)
    dev = hass.data[DOMAIN][DEVICES].get(device_id)
    if dev:
        dev.set_customize(customize)
        if ip_address is not None:
            dev.set_ip_address(ip_address)
        if refresh_interval is not None:
            dev.set_refresh_interval(refresh_interval)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    attributes = []
    for device_entities in MIDEA_DEVICES.values():
        for attribute_name, attribute in cast(
            dict,
            device_entities["entities"],
        ).items():
            if (
                attribute.get("type") in EXTRA_SWITCH
                and attribute_name.value not in attributes
            ):
                attributes.append(attribute_name.value)

    def service_set_attribute(service: Any) -> None:
        device_id = service.data["device_id"]
        attr = service.data["attribute"]
        value = service.data["value"]
        dev = hass.data[DOMAIN][DEVICES].get(device_id)
        if dev:
            if attr == "fan_speed" and value == "auto":
                value = 102
            item = None
            if _dev := MIDEA_DEVICES.get(dev.device_type):
                item = cast(dict, _dev["entities"]).get(attr)
            if (
                item
                and (item.get("type") in EXTRA_SWITCH)
                or (
                    dev.device_type == 0xAC
                    and attr == "fan_speed"
                    and value in range(103)
                )
            ):
                dev.set_attribute(attr=attr, value=value)
            else:
                _LOGGER.error(
                    "Appliance [%s] has no attribute %s or value is invalid",
                    device_id,
                    attr,
                )

    def service_send_command(service: Any) -> None:
        device_id = service.data.get("device_id")
        cmd_type = service.data.get("cmd_type")
        cmd_body = service.data.get("cmd_body")
        try:
            cmd_body = bytearray.fromhex(cmd_body)
        except ValueError:
            _LOGGER.error(
                "Appliance [%s] invalid cmd_body, a hexadecimal string required",
                device_id,
            )
            return
        dev = hass.data[DOMAIN][DEVICES].get(device_id)
        if dev:
            dev.send_command(cmd_type, cmd_body)

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


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        return True
    name = config_entry.data.get(CONF_NAME)
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if name is None:
        name = f"{device_id}"
    if device_type is None:
        device_type = 0xAC
    token = config_entry.data.get(CONF_TOKEN)
    key = config_entry.data.get(CONF_KEY)
    ip_address = config_entry.options.get(CONF_IP_ADDRESS, None)
    if ip_address is None:
        ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    refresh_interval = config_entry.options.get(CONF_REFRESH_INTERVAL)
    port = config_entry.data.get(CONF_PORT)
    model = config_entry.data.get(CONF_MODEL)
    subtype = config_entry.data.get(CONF_SUBTYPE, 0)
    protocol = config_entry.data.get(CONF_PROTOCOL)
    customize = config_entry.options.get(CONF_CUSTOMIZE)
    if protocol == 3 and (key is None or key is None):
        _LOGGER.error("For V3 devices, the key and the token is required.")
        return False
    if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 3):
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
        )
    else:
        device = device_selector(
            name=name,
            device_id=device_id,
            device_type=device_type,
            ip_address=ip_address,
            port=port,
            token=token,
            key=key,
            protocol=protocol,
            model=model,
            subtype=subtype,
            customize=customize,
        )
    if refresh_interval is not None:
        device.set_refresh_interval(refresh_interval)
    if device:
        device.open()
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        if DEVICES not in hass.data[DOMAIN]:
            hass.data[DOMAIN][DEVICES] = {}
        hass.data[DOMAIN][DEVICES][device_id] = device
        for platform in ALL_PLATFORM:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(config_entry, platform),
            )
        config_entry.add_update_listener(update_listener)
        return True
    return False


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    device_type = config_entry.data.get(CONF_TYPE)
    if device_type == CONF_ACCOUNT:
        return True
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    if device_id is not None:
        dm = hass.data[DOMAIN][DEVICES].get(device_id)
        if dm is not None:
            dm.close()
        hass.data[DOMAIN][DEVICES].pop(device_id)
    for platform in ALL_PLATFORM:
        await hass.config_entries.async_forward_entry_unload(config_entry, platform)
    return True
