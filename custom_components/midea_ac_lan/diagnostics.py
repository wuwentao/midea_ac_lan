"""Diagnostics support for Midea AC LAN."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_TOKEN,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

from .const import CONF_ACCOUNT, CONF_KEY

# CONF_ACCOUNT / CONF_PASSWORD are the Midea cloud email and password the E3
# usage-report option flow persists into the config-entry options, so they must
# be redacted from the diagnostics export alongside the per-device token/key.
TO_REDACT = {CONF_TOKEN, CONF_KEY, CONF_ACCOUNT, CONF_PASSWORD}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # ruff:ignore[unused-function-argument]
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Returns
    -------
    Dictionary of config

    """
    return {"entry": async_redact_data(entry.as_dict(), TO_REDACT)}
