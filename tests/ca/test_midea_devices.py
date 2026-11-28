"""Tests for CA-specific device metadata."""

import asyncio
import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock

from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES
from midealan.const import DeviceType

from custom_components.midea_ac_lan.const import (
    DEVICES,
    DOMAIN,
    normalize_entity_options,
    supports_device,
)
from custom_components.midea_ac_lan.midea_devices import MIDEA_DEVICES
from custom_components.midea_ac_lan.switch import MideaSwitch, async_setup_entry

TRANSLATIONS_DIR = (
    Path(__file__).parents[2] / "custom_components" / "midea_ac_lan" / "translations"
)


def test_ca_mode_switch_translations_exist_in_all_locales() -> None:
    """Require localized names for every CA refrigerator mode switch."""
    entities = cast(
        "dict[str, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.CA]["entities"],
    )
    expected = {
        "storage_mode": (
            "storage_mode",
            "storage_mode",
            "refrigeracao_rapida",
            "switch.151732607632612_refrigeracao_rapida",
        ),
        "freezing_mode": (
            "freezing_mode",
            "freezing_mode",
            "congelamento_rapido",
            "switch.151732607632612_congelamento_rapido",
        ),
        "holiday_mode": (
            "holiday_mode",
            None,
            "modo_ferias",
            "switch.151732607632612_modo_ferias",
        ),
    }
    for entity_key, (attribute, translation_key, alias, _) in expected.items():
        config = entities[entity_key]
        assert config["attribute"] == attribute
        if translation_key is None:
            assert "translation_key" not in config
            assert config["name"] == "Modo Férias"
        else:
            assert config["translation_key"] == translation_key
        assert config["option_aliases"] == [alias]
        assert config["default"] is False
        assert supports_device("310Z999Z", 56, config)
        assert not supports_device("OTHER", 56, config)
        assert not supports_device("310Z999Z", 57, config)
    for translation_file in TRANSLATIONS_DIR.glob("*.json"):
        translation = json.loads(translation_file.read_text(encoding="utf-8"))
        switches = translation["entity"]["switch"]
        for _, translation_key, _, _ in expected.values():
            if translation_key is None:
                continue
            assert switches[translation_key]["name"]


def test_ca_switches_keep_original_unique_ids_and_display_names() -> None:
    """Use the prior stable identity keys and Portuguese translation labels."""
    device = Mock()
    device.device_type = DeviceType.CA
    device.device_id = 151732607632612
    device.name = "Geladeira"

    expected_unique_ids = {
        "storage_mode": "midea_ac_lan.151732607632612_storage_mode",
        "freezing_mode": "midea_ac_lan.151732607632612_freezing_mode",
        "holiday_mode": "midea_ac_lan.151732607632612_holiday_mode",
    }
    for entity_key, expected_unique_id in expected_unique_ids.items():
        entity = MideaSwitch(device, entity_key)
        assert entity.unique_id == expected_unique_id
        assert expected_unique_id.startswith(f"{DOMAIN}.")
        assert entity._entity_key == entity_key
        if entity_key == "holiday_mode":
            assert entity._attr_name == "Modo Férias"


def test_legacy_switch_options_map_to_canonical_keys_without_dropping_others() -> None:
    """Preserve old opt-ins and unrelated options through the options flow."""
    entities = cast(
        "dict[str, dict[str, object]]",
        MIDEA_DEVICES[DeviceType.CA]["entities"],
    )
    selected = normalize_entity_options(
        {
            "refrigeracao_rapida",
            "congelamento_rapido",
            "modo_ferias",
            "existing_optional_switch",
        },
        entities,
    )

    assert selected == {
        "storage_mode",
        "freezing_mode",
        "holiday_mode",
        "refrigeracao_rapida",
        "congelamento_rapido",
        "modo_ferias",
        "existing_optional_switch",
    }


def test_switch_setup_preserves_legacy_ca_mode_opt_ins() -> None:
    """Create the original three controls from the stored Portuguese options."""
    device = Mock()
    device.device_type = DeviceType.CA
    device.device_id = 151732607632612
    device.name = "Geladeira"
    device.model = "310Z999Z"
    device.subtype = 56
    device.attributes = {}

    hass = Mock()
    hass.data = {DOMAIN: {DEVICES: {device.device_id: device}}}
    config_entry = Mock()
    config_entry.data = {CONF_DEVICE_ID: device.device_id}
    config_entry.options = {
        CONF_SWITCHES: [
            "refrigeracao_rapida",
            "congelamento_rapido",
            "modo_ferias",
            "unrelated_stale_option",
        ],
    }
    add_entities = Mock()

    asyncio.run(async_setup_entry(hass, config_entry, add_entities))

    entities = add_entities.call_args.args[0]
    assert {entity.unique_id for entity in entities} == {
        "midea_ac_lan.151732607632612_storage_mode",
        "midea_ac_lan.151732607632612_freezing_mode",
        "midea_ac_lan.151732607632612_holiday_mode",
    }
