"""Diagnostics support for Midea AC LAN."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import (
    CONF_TOKEN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import CONF_KEY

TO_REDACT = {CONF_TOKEN, CONF_KEY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Returns
    -------
    Dictiory of config

    """
    return {"entry": async_redact_data(entry.as_dict(), TO_REDACT)}
