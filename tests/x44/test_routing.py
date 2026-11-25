"""Model-specific entity setup and options for devices advertising 0x44."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from homeassistant.const import (
    CONF_DEVICE,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_SWITCHES,
    CONF_TYPE,
)
from homeassistant.core import HomeAssistant
from midealan.device import DeviceType, MideaDevice
from midealan.devices import x44

from custom_components.midea_ac_lan import x44_entity_type
from custom_components.midea_ac_lan.config_flow import (
    MideaLanConfigFlow,
    MideaLanOptionsFlowHandler,
)
from custom_components.midea_ac_lan.const import CONF_MODEL, CONF_SN8, DEVICES, DOMAIN
from tests.conftest import setup_integration
from tests.ha import MockConfigEntry


async def test_discovered_panel_labels(hass: HomeAssistant) -> None:
    """Label the selectable devices using the model reported by LAN discovery."""
    flow = MideaLanConfigFlow()
    flow.hass = hass
    devices = {
        i: {
            CONF_TYPE: DeviceType.X44,
            CONF_MODEL: model,
            CONF_IP_ADDRESS: f"192.0.2.{i}",
        }
        for i, model in enumerate(("115P0303", "404M0001", "TEST0001"), start=1)
    }
    with patch(
        "custom_components.midea_ac_lan.config_flow.discover",
        return_value=devices,
    ):
        form = await flow.async_step_discovery({CONF_IP_ADDRESS: "auto"})
        listing = await flow.async_step_list()
    kjr = "KJR 90S" if hasattr(x44, "resolve_profile") else "Smart Panel"
    assert form["data_schema"].schema[CONF_DEVICE].container == {
        1: f"1 ({kjr})",
        2: "2 (ZKP 3 Inch)",
        3: "3 (Smart Panel)",
    }
    rows = listing["description_placeholders"]["table"].splitlines()[2:]
    assert [row.split("|")[1] for row in rows] == [
        f"44 ({kjr})",
        "44 (ZKP 3 Inch)",
        "44 (Smart Panel)",
    ]


@pytest.mark.usefixtures("enable_integration")
@pytest.mark.parametrize(
    ("language", "model", "device_name", "expected"),
    [
        ("zh-Hans", "115P0303", None, "KJR 90S"),
        ("zh-Hans", "404M0001", None, "ZKP 3 Inch"),
        ("en", "115P0303", None, "KJR 90S"),
        ("en", "404M0001", None, "ZKP 3 Inch"),
        ("de", "404M0001", None, "ZKP 3 Inch"),
        ("zh-Hans", "404M0001", "客厅", "客厅"),
        ("zh-Hans", "TEST0001", None, "Smart Panel"),
    ],
)
async def test_panel_name_form_default(
    hass: HomeAssistant,
    language: str,
    model: str,
    device_name: str | None,
    expected: str,
) -> None:
    """Use the same model name in every language unless the device has a name."""
    hass.config.language = language
    flow = MideaLanConfigFlow()
    flow.hass = hass
    flow.found_device = {
        CONF_TYPE: DeviceType.X44,
        CONF_SN8: model,
        CONF_NAME: device_name,
    }
    form = await flow.async_step_manually()
    field = next(key for key in form["data_schema"].schema if key == CONF_NAME)
    if model == "115P0303" and not hasattr(x44, "resolve_profile"):
        expected = "Smart Panel"
    assert field.default() == expected


def test_library_profile_selects_an_existing_table() -> None:
    """Only the screen and recognized delegated types have HA entity definitions."""
    data = {CONF_MODEL: "404m0001", CONF_SN8: "00000000"}
    with patch.object(x44, "resolve_profile", None, create=True):
        assert x44_entity_type(data) == DeviceType.X44
        assert x44_entity_type({**data, CONF_SN8: "115P0303"}) is None

    for profile, expected in (
        (SimpleNamespace(name="ZKP-3INCH01"), DeviceType.X44),
        (SimpleNamespace(device_type=DeviceType.AC), DeviceType.AC),
        (SimpleNamespace(device_type=0xFFFF), None),
        (SimpleNamespace(name="Other panel"), None),
        (None, None),
    ):
        with patch.object(
            x44,
            "resolve_profile",
            return_value=profile,
            create=True,
        ) as resolve:
            assert x44_entity_type(data) == expected
            resolve.assert_called_once_with("404m0001", 0, "00000000")


@pytest.mark.usefixtures("enable_integration")
@pytest.mark.parametrize(
    ("model", "sn8", "expected"),
    [
        ("404M0001", None, DeviceType.X44),
        (None, "115P0303", DeviceType.AC),
        ("404M0001", "115P0303", None),
        ("TEST0001", None, None),
    ],
)
async def test_saved_panel(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    model: str | None,
    sn8: str | None,
    expected: DeviceType | None,
) -> None:
    """Discovery, offline options and the loaded entities agree on the model."""
    if expected == DeviceType.AC and not hasattr(x44, "resolve_profile"):
        expected = None  # The pre-routing library cannot operate this panel.
    data = {
        **config_entry.data,
        CONF_TYPE: DeviceType.X44,
        CONF_MODEL: model,
        CONF_SN8: sn8,
    }
    hass.config_entries.async_update_entry(config_entry, data=data)
    device_id = data[CONF_DEVICE_ID]

    flow = MideaLanConfigFlow()
    flow.hass = hass
    with patch(
        "custom_components.midea_ac_lan.config_flow.discover",
        return_value={device_id: data},
    ):
        listing = await flow.async_step_list()
    assert ("YES" in listing["description_placeholders"]["table"]) == (
        expected is not None
    )
    options = MideaLanOptionsFlowHandler(config_entry)
    options.hass = hass
    schema = (await options.async_step_init())["data_schema"].schema
    switches = schema[CONF_SWITCHES].options if CONF_SWITCHES in schema else {}
    assert ("eco_mode" in switches) == (expected == DeviceType.AC)
    assert ("left_button" in switches) == (expected == DeviceType.X44)

    with patch.object(MideaDevice, "open", autospec=True) as opened:
        await setup_integration(hass, config_entry)
    assert opened.call_count == int(expected is not None)
    assert bool(hass.states.get(f"climate.{device_id}_climate")) == (
        expected == DeviceType.AC
    )
    assert bool(hass.states.get(f"number.{device_id}_voice_volume")) == (
        expected == DeviceType.X44
    )
    assert (device_id in hass.data[DOMAIN][DEVICES]) == (expected is not None)
    assert config_entry.data[CONF_TYPE] == DeviceType.X44
    assert await hass.config_entries.async_unload(config_entry.entry_id)
