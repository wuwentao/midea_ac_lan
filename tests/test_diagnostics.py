"""Tests for config entry diagnostics."""

from unittest.mock import Mock

from homeassistant.const import CONF_TOKEN

from custom_components.midea_ac_lan.const import CONF_KEY
from custom_components.midea_ac_lan.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redacts_authentication_material() -> None:
    """Preserve useful entry data while redacting Token and Key values."""
    entry = Mock()
    entry.as_dict.return_value = {
        "data": {CONF_TOKEN: "token", CONF_KEY: "key", "name": "Appliance"},
    }

    result = await async_get_config_entry_diagnostics(Mock(), entry)

    assert result == {
        "entry": {
            "data": {
                CONF_TOKEN: "**REDACTED**",
                CONF_KEY: "**REDACTED**",
                "name": "Appliance",
            },
        },
    }
