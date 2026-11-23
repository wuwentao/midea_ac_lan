"""Tests for config entry diagnostics."""

from unittest.mock import Mock

from homeassistant.const import CONF_PASSWORD, CONF_TOKEN

from custom_components.midea_ac_lan.const import CONF_ACCOUNT, CONF_KEY
from custom_components.midea_ac_lan.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_redacts_authentication_material() -> None:
    """Preserve useful entry data while redacting credentials.

    Token and Key live in ``data``; the E3 usage-report option flow persists
    the Midea cloud account and password into ``options``, so both locations
    must be redacted from the export.
    """
    entry = Mock()
    entry.as_dict.return_value = {
        "data": {CONF_TOKEN: "token", CONF_KEY: "key", "name": "Appliance"},
        "options": {
            CONF_ACCOUNT: "user@example.com",
            CONF_PASSWORD: "secret",
            "refresh": 60,
        },
    }

    result = await async_get_config_entry_diagnostics(Mock(), entry)

    assert result == {
        "entry": {
            "data": {
                CONF_TOKEN: "**REDACTED**",
                CONF_KEY: "**REDACTED**",
                "name": "Appliance",
            },
            "options": {
                CONF_ACCOUNT: "**REDACTED**",
                CONF_PASSWORD: "**REDACTED**",
                "refresh": 60,
            },
        },
    }
