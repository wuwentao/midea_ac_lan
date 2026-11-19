"""Tests for Midea climate entities."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
    PRESET_SLEEP,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_ON,
    SWING_VERTICAL,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    Platform,
)
from midealan.device import DeviceType
from midealan.devices.ac import DeviceAttributes as ACAttributes
from midealan.devices.c1 import DeviceAttributes as C1Attributes
from midealan.devices.c3 import DeviceAttributes as C3Attributes
from midealan.devices.cc import DeviceAttributes as CCAttributes
from midealan.devices.cf import DeviceAttributes as CFAttributes
from midealan.devices.ed import DeviceAttributes as EDAttributes
from midealan.devices.fb import DeviceAttributes as FBAttributes

import custom_components.midea_ac_lan.climate as climate_module
from custom_components.midea_ac_lan.climate import (
    FAN_FULL_SPEED,
    FAN_SILENT,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    MideaACClimate,
    MideaC1Climate,
    MideaC3Climate,
    MideaCCClimate,
    MideaCFClimate,
    MideaClimate,
    MideaEDTeaBarClimate,
    MideaFBClimate,
    async_setup_entry,
)

from .helpers import DeviceFactory, InstallConfig, setup_context

BASE_FEATURES = (
    ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.FAN_MODE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.SWING_MODE
    | ClimateEntityFeature.TURN_OFF
    | ClimateEntityFeature.TURN_ON
)
TARGET_AND_POWER_FEATURES = (
    ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.TURN_OFF
    | ClimateEntityFeature.TURN_ON
)
DEFAULT_FAN_MODES = [
    FAN_SILENT,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_FULL_SPEED,
    FAN_AUTO,
]


def config_entry(**options: object) -> SimpleNamespace:
    """Build the options surface used by climate constructors."""
    return SimpleNamespace(options=options)


def make_ac(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    *,
    attributes: dict[object, object] | None = None,
    capabilities: object = None,
    **options: object,
) -> tuple[MideaACClimate, Mock, dict[object, object]]:
    """Build an AC climate with explicit capabilities."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.AC)
    device, values = device_factory(
        device_type=DeviceType.AC,
        attributes=attributes,
    )
    device.capabilities = {} if capabilities is None else capabilities
    device.temperature_step = 0.5
    return MideaACClimate(device, "main", config_entry(**options)), device, values


@pytest.mark.parametrize(
    ("device_type", "expected_class"),
    [
        (DeviceType.AC, MideaACClimate),
        (DeviceType.CC, MideaCCClimate),
        (DeviceType.CF, MideaCFClimate),
        (DeviceType.C3, MideaC3Climate),
        (DeviceType.C1, MideaC1Climate),
        (DeviceType.FB, MideaFBClimate),
        (DeviceType.ED, MideaEDTeaBarClimate),
    ],
)
async def test_async_setup_entry_device_classes(
    device_type: int,
    expected_class: type[MideaClimate] | type[MideaEDTeaBarClimate],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Select every supported climate implementation and filter configs."""
    config: dict[str, object] = {"type": Platform.CLIMATE, "default": True}
    selected: dict[str, object] = {"type": Platform.CLIMATE}
    if device_type == DeviceType.C3:
        config["zone"] = 0
        selected["zone"] = 1
    install_config(
        {
            "main": config,
            "selected": selected,
            "ignored": {"type": Platform.CLIMATE},
            "unsupported": {
                "type": Platform.CLIMATE,
                "default": True,
                "models": ["OTHER"],
            },
            "wrong": {"type": Platform.SENSOR, "default": True},
        },
        device_type,
    )
    device, _ = device_factory(device_type=device_type)
    device.capabilities = {}
    device.temperature_step = 1
    device.fan_modes = [FAN_AUTO]
    device.heating_modes = ["user"]
    device.modes = ["manual"]
    hass, entry, add_entities = setup_context(device, switches=["selected"])
    await async_setup_entry(hass, entry, add_entities)
    entities = add_entities.call_args.args[0]
    assert [type(item) for item in entities] == [expected_class, expected_class]
    assert [item._entity_key for item in entities] == ["main", "selected"]
    if device_type == DeviceType.C3:
        assert [item._zone for item in entities] == [0, 1]


async def test_async_setup_entry_unknown_device(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Ignore climate configs for unsupported device types."""
    install_config({"main": {"type": Platform.CLIMATE, "default": True}})
    device, _ = device_factory()
    hass, entry, add_entities = setup_context(device)
    await async_setup_entry(hass, entry, add_entities)
    add_entities.assert_called_once_with([])


@pytest.mark.parametrize(
    ("attributes", "expected"),
    [
        ({"comfort_mode": True}, PRESET_COMFORT),
        ({"eco_mode": True}, PRESET_ECO),
        ({"boost_mode": True}, PRESET_BOOST),
        ({"sleep_mode": True}, PRESET_SLEEP),
        ({"frost_protect": True}, PRESET_AWAY),
        ({"comfort_mode": True, "eco_mode": True}, PRESET_COMFORT),
        ({"eco_mode": True, "boost_mode": True}, PRESET_ECO),
        ({"boost_mode": True, "sleep_mode": True}, PRESET_BOOST),
        ({"sleep_mode": True, "frost_protect": True}, PRESET_SLEEP),
        ({}, PRESET_NONE),
    ],
)
def test_base_properties_and_preset_priority(
    attributes: dict[str, bool],
    expected: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose base state and resolve preset flags in priority order."""
    install_config({"main": {"type": Platform.CLIMATE}})
    state = {
        "power": True,
        "mode": 1,
        "target_temperature": 22.5,
        "indoor_temperature": 21.0,
        **attributes,
    }
    device, values = device_factory(attributes=state)
    entity = MideaClimate(device, "main")
    entity._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]
    assert entity.supported_features == BASE_FEATURES
    assert entity.hvac_mode is HVACMode.COOL
    assert entity.native_target_temperature == pytest.approx(22.5)
    assert entity.native_current_temperature == pytest.approx(21.0)
    assert entity.preset_mode == expected
    assert entity.extra_state_attributes is values
    values["power"] = False
    assert entity.hvac_mode is HVACMode.OFF
    values["power"] = True
    values["mode"] = -1
    assert entity.hvac_mode is HVACMode.OFF
    values["mode"] = 2
    assert entity.hvac_mode is HVACMode.OFF


def test_base_commands(
    caplog: pytest.LogCaptureFixture,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Dispatch base temperature, HVAC, power, and update commands."""
    install_config({"main": {"type": Platform.CLIMATE}})
    device, _ = device_factory(attributes={})
    entity = MideaClimate(device, "main")
    entity._attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL]
    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: 22.26})
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 23, ATTR_HVAC_MODE: HVACMode.COOL},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 24, ATTR_HVAC_MODE: HVACMode.OFF},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 25, ATTR_HVAC_MODE: HVACMode.HEAT},
    )
    assert device.set_target_temperature.call_args_list == [
        call(target_temperature=22.5, mode=None, zone=None),
        call(target_temperature=23.0, mode=1, zone=None),
    ]
    entity.set_hvac_mode(HVACMode.COOL)
    entity.set_hvac_mode(HVACMode.OFF)
    entity.turn_on()
    entity.turn_off()
    assert device.set_attribute.call_args_list == [
        call(attr="power", value=False),
        call(attr="mode", value=1),
        call(attr="power", value=False),
        call(attr="power", value=True),
        call(attr="power", value=False),
    ]
    assert "Error setting temperature" in caplog.text

    entity.hass = SimpleNamespace()
    entity.schedule_update_if_running = Mock()
    entity.update_state({})
    entity.schedule_update_if_running.assert_called_once_with()
    detached = MideaClimate(device, "main")
    detached.schedule_update_if_running = Mock()
    detached.update_state({})
    detached.schedule_update_if_running.assert_not_called()
    assert "Climate update_state skipped for None" in caplog.text


@pytest.mark.parametrize(
    ("requested", "attribute", "value"),
    [
        (PRESET_AWAY, "frost_protect", True),
        (PRESET_COMFORT, "comfort_mode", True),
        (PRESET_SLEEP, "sleep_mode", True),
        (PRESET_ECO, "eco_mode", True),
        (PRESET_BOOST, "boost_mode", True),
    ],
)
def test_base_enable_presets(
    requested: str,
    attribute: str,
    value: bool,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Enable each supported preset flag."""
    install_config({"main": {"type": Platform.CLIMATE}})
    device, _ = device_factory(attributes={})
    MideaClimate(device, "main").set_preset_mode(requested.upper())
    device.set_attribute.assert_called_once_with(attr=attribute, value=value)


@pytest.mark.parametrize(
    ("active", "attribute"),
    [
        ("frost_protect", "frost_protect"),
        ("comfort_mode", "comfort_mode"),
        ("sleep_mode", "sleep_mode"),
        ("eco_mode", "eco_mode"),
        ("boost_mode", "boost_mode"),
    ],
)
def test_base_disable_presets(
    active: str,
    attribute: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Disable the currently active preset when selecting none."""
    install_config({"main": {"type": Platform.CLIMATE}})
    device, _ = device_factory(attributes={active: True})
    MideaClimate(device, "main").set_preset_mode(PRESET_NONE)
    device.set_attribute.assert_called_once_with(attr=attribute, value=False)


def test_base_unsupported_preset_has_no_command(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Ignore an unsupported preset when no known preset is active."""
    install_config({"main": {"type": Platform.CLIMATE}})
    device, _ = device_factory(attributes={})
    MideaClimate(device, "main").set_preset_mode("invalid")
    device.set_attribute.assert_not_called()


def test_tea_bar_climate(
    caplog: pytest.LogCaptureFixture,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map tea-bar state, commands, features, and update callbacks."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.ED)
    device, values = device_factory(
        device_type=DeviceType.ED,
        attributes={
            EDAttributes.boiling: False,
            EDAttributes.dispensing: False,
            EDAttributes.current_temperature: 60,
            EDAttributes.target_temperature: 85,
            EDAttributes.heating: True,
            EDAttributes.keep_warm_remaining: 10,
        },
    )
    entity = MideaEDTeaBarClimate(device, "main")
    assert entity.supported_features == TARGET_AND_POWER_FEATURES
    assert entity.hvac_mode is HVACMode.OFF
    assert entity.hvac_action is HVACAction.OFF
    values[EDAttributes.boiling] = True
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.hvac_action is HVACAction.HEATING
    values[EDAttributes.boiling] = False
    values[EDAttributes.dispensing] = True
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.hvac_action is HVACAction.HEATING
    assert entity.native_current_temperature == 60
    assert entity.native_target_temperature == 85
    assert entity.extra_state_attributes == {
        str(EDAttributes.heating): True,
        str(EDAttributes.dispensing): True,
        str(EDAttributes.keep_warm_remaining): 10,
    }
    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: "90"})
    entity.set_hvac_mode(HVACMode.HEAT)
    entity.set_hvac_mode(HVACMode.OFF)
    entity.set_hvac_mode(HVACMode.COOL)
    assert device.set_attribute.call_args_list == [
        call(EDAttributes.boil_temperature, 90.0),
        call(EDAttributes.boiling, True),
        call(EDAttributes.boiling, False),
    ]
    assert "Ignoring unsupported tea bar HVAC mode" in caplog.text
    entity.hass = SimpleNamespace()
    entity.schedule_update_if_running = Mock()
    entity.update_state({})
    entity.schedule_update_if_running.assert_called_once_with()
    detached = MideaEDTeaBarClimate(device, "main")
    detached.update_state({})
    assert "Climate update_state skipped for None" in caplog.text


@pytest.mark.parametrize(
    (
        "customize",
        "expected_swing",
        "expected_hvac",
        "expected_presets",
        "expected_fans",
    ),
    [
        ("", None, None, None, None),
        ("not-json", None, None, None, None),
        (json.dumps([]), None, None, None, None),
        (json.dumps({}), None, None, None, None),
        (
            json.dumps(
                {
                    "swing": 0,
                    "hvac_modes": ["cool", "cool", "invalid"],
                    "preset_modes": [PRESET_ECO, PRESET_ECO, "invalid"],
                    "fan_modes": [FAN_LOW, FAN_LOW, "invalid"],
                },
            ),
            False,
            [HVACMode.OFF, HVACMode.COOL],
            [PRESET_NONE, PRESET_ECO],
            [FAN_LOW],
        ),
        (
            json.dumps(
                {
                    "swing": True,
                    "hvac_modes": ["off"],
                    "preset_modes": [],
                    "fan_modes": [],
                },
            ),
            True,
            None,
            [PRESET_NONE],
            None,
        ),
        (
            json.dumps(
                {
                    "hvac_modes": "invalid",
                    "preset_modes": [PRESET_NONE],
                    "fan_modes": "invalid",
                },
            ),
            None,
            None,
            [PRESET_NONE],
            None,
        ),
    ],
)
def test_ac_customize_parsing(
    customize: str,
    expected_swing: bool | None,
    expected_hvac: list[HVACMode] | None,
    expected_presets: list[str] | None,
    expected_fans: list[str] | None,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Parse valid capability overrides and ignore malformed values."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        customize=customize,
    )
    assert entity._customize_swing is expected_swing
    assert entity._customize_hvac_modes == expected_hvac
    assert entity._customize_preset_modes == expected_presets
    assert entity._customize_fan_modes == expected_fans


@pytest.mark.parametrize(
    ("capabilities", "expected"),
    [
        ("invalid", True),
        ({}, True),
        ({"swing_modes": "invalid"}, True),
        ({"swing_modes": []}, False),
        ({"swing_modes": ["vertical"]}, True),
        ({"swing_modes": ["horizontal"]}, True),
    ],
)
def test_ac_swing_capability(
    capabilities: object,
    expected: bool,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Interpret B5 swing capability profiles."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        capabilities=capabilities,
    )
    assert entity._capability_swing() is expected


def test_ac_capability_and_customize_priority(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Prefer customize values and filter B5 modes and presets."""
    capabilities = {
        "modes": ["auto", "cool", "dry", "heat"],
        "eco": True,
        "turbo_heat": True,
        "swing_modes": [],
    }
    entity, device, _ = make_ac(
        device_factory,
        install_config,
        capabilities=capabilities,
    )
    assert entity.hvac_modes == [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.COOL,
        HVACMode.DRY,
        HVACMode.HEAT,
        HVACMode.FAN_ONLY,
    ]
    assert entity.preset_modes == [
        PRESET_NONE,
        PRESET_COMFORT,
        PRESET_ECO,
        PRESET_BOOST,
        PRESET_SLEEP,
        PRESET_AWAY,
    ]
    assert not entity.supported_features & ClimateEntityFeature.SWING_MODE
    device.capabilities = {"modes": ["cool"], "eco": False}
    assert entity.hvac_modes == [HVACMode.OFF, HVACMode.COOL, HVACMode.FAN_ONLY]
    assert entity.preset_modes == [PRESET_NONE, PRESET_COMFORT, PRESET_SLEEP]
    device.capabilities = {"modes": ["heat"]}
    assert entity.hvac_modes == [HVACMode.OFF, HVACMode.HEAT, HVACMode.FAN_ONLY]

    customized, _, _ = make_ac(
        device_factory,
        install_config,
        capabilities=capabilities,
        customize=json.dumps(
            {
                "swing": True,
                "hvac_modes": ["heat"],
                "preset_modes": [],
            },
        ),
    )
    assert customized.hvac_modes == [HVACMode.OFF, HVACMode.HEAT]
    assert customized.preset_modes == [PRESET_NONE]
    assert customized.supported_features & ClimateEntityFeature.SWING_MODE
    assert not customized.supported_features & ClimateEntityFeature.PRESET_MODE


@pytest.mark.parametrize(
    ("capabilities", "expected_presets"),
    [
        (
            "invalid",
            [
                PRESET_NONE,
                PRESET_COMFORT,
                PRESET_ECO,
                PRESET_BOOST,
                PRESET_SLEEP,
                PRESET_AWAY,
            ],
        ),
        (
            {},
            [
                PRESET_NONE,
                PRESET_COMFORT,
                PRESET_ECO,
                PRESET_BOOST,
                PRESET_SLEEP,
                PRESET_AWAY,
            ],
        ),
        ({"modes": "invalid"}, [PRESET_NONE, PRESET_COMFORT, PRESET_SLEEP]),
    ],
)
def test_ac_invalid_capability_defaults(
    capabilities: object,
    expected_presets: list[str],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Use the complete default mode and preset sets for invalid B5 data."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        capabilities=capabilities,
    )
    default_hvac = [
        HVACMode.OFF,
        HVACMode.AUTO,
        HVACMode.COOL,
        HVACMode.DRY,
        HVACMode.HEAT,
        HVACMode.FAN_ONLY,
    ]
    assert entity.hvac_modes == default_hvac
    assert entity.preset_modes == expected_presets


@pytest.mark.parametrize(
    ("speed", "expected"),
    [
        (10, FAN_SILENT),
        (30, FAN_LOW),
        (50, FAN_MEDIUM),
        (70, FAN_HIGH),
        (90, FAN_FULL_SPEED),
        (110, FAN_AUTO),
    ],
)
def test_ac_fan_mode_thresholds(
    speed: int,
    expected: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map raw fan speeds into stable HA fan modes."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={ACAttributes.fan_speed: speed},
    )
    assert entity.fan_mode == expected


@pytest.mark.parametrize(
    ("capabilities", "expected"),
    [
        ("invalid", DEFAULT_FAN_MODES),
        ({}, DEFAULT_FAN_MODES),
        ({"fan_speeds": "invalid"}, DEFAULT_FAN_MODES),
        ({"fan_speeds": ["custom"]}, DEFAULT_FAN_MODES),
        ({"fan_speeds": ["low", "auto"]}, [FAN_LOW, FAN_AUTO]),
        ({"fan_speeds": []}, DEFAULT_FAN_MODES),
    ],
)
def test_ac_fan_modes_from_capabilities(
    capabilities: object,
    expected: list[str],
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map B5 fan profiles and fall back for unusable profiles."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        capabilities=capabilities,
    )
    assert entity.fan_modes == expected


def test_ac_fan_mode_fallbacks(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Fall back to auto or the first exposed fan mode."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={ACAttributes.fan_speed: 10},
        capabilities={"fan_speeds": ["auto"]},
    )
    assert entity.fan_mode == FAN_AUTO
    entity._customize_fan_modes = [FAN_HIGH]
    assert entity.fan_mode == FAN_HIGH


def test_ac_state_and_commands(
    caplog: pytest.LogCaptureFixture,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map AC state, limits, precision, humidity, swing, and commands."""
    attributes: dict[object, object] = {
        "power": True,
        "mode": 4,
        ACAttributes.fan_speed: 60,
        ACAttributes.swing_vertical: True,
        ACAttributes.swing_horizontal: True,
        ACAttributes.outdoor_temperature: 8,
        ACAttributes.min_temperature: None,
        ACAttributes.max_temperature: None,
        "indoor_humidity": 50,
    }
    entity, device, values = make_ac(
        device_factory,
        install_config,
        attributes=attributes,
        sensors=["indoor_humidity"],
    )
    assert entity.hvac_mode is HVACMode.HEAT
    values["mode"] = 6
    assert entity.hvac_mode is HVACMode.OFF
    values["mode"] = -1
    assert entity.hvac_mode is HVACMode.OFF
    values["power"] = False
    assert entity.hvac_mode is HVACMode.OFF
    assert entity.target_temperature_step == PRECISION_HALVES
    device.temperature_step = 1
    assert entity.target_temperature_step == PRECISION_WHOLE
    assert entity.swing_mode == SWING_BOTH
    assert entity.current_humidity == pytest.approx(50.0)
    assert entity.outdoor_temperature == 8
    assert entity.min_temp == TEMPERATURE_MIN
    assert entity.max_temp == TEMPERATURE_MAX
    values[ACAttributes.min_temperature] = 10
    values[ACAttributes.max_temperature] = 35
    assert entity.min_temp == 10
    assert entity.max_temp == 35

    entity.set_hvac_mode(HVACMode.HEAT)
    entity.set_hvac_mode(HVACMode.OFF)
    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: 22.26})
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 23, ATTR_HVAC_MODE: HVACMode.COOL},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 24, ATTR_HVAC_MODE: HVACMode.OFF},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 25, ATTR_HVAC_MODE: "invalid"},
    )
    entity.set_fan_mode(FAN_HIGH)
    entity.set_fan_mode("invalid")
    entity.set_swing_mode(SWING_HORIZONTAL)
    assert device.set_attribute.call_args_list == [
        call(attr="mode", value=4),
        call(attr="power", value=False),
        call(attr="power", value=False),
        call(attr=ACAttributes.fan_speed, value=80),
    ]
    assert device.set_target_temperature.call_args_list == [
        call(target_temperature=22.5, mode=None, zone=None),
        call(target_temperature=23.0, mode=2, zone=None),
    ]
    device.set_swing.assert_called_once_with(
        swing_vertical=False,
        swing_horizontal=True,
    )
    assert "Error setting temperature" in caplog.text


@pytest.mark.parametrize(
    ("power", "mode", "frequency", "expected"),
    [
        (False, 4, 50, HVACAction.OFF),
        (True, 0, 50, HVACAction.OFF),
        (True, 5, None, HVACAction.FAN),
        (True, 5, 0, HVACAction.FAN),
        (True, 2, None, None),
        (True, 2, 0, HVACAction.IDLE),
        (True, 2, 50, HVACAction.COOLING),
        (True, 3, 0, HVACAction.IDLE),
        (True, 3, 50, HVACAction.DRYING),
        (True, 4, 0, HVACAction.IDLE),
        (True, 4, 50, HVACAction.HEATING),
        (True, 1, 0, HVACAction.IDLE),
        (True, 1, 50, None),
    ],
)
def test_ac_hvac_action(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    power: bool,
    mode: int,
    frequency: int | None,
    expected: HVACAction | None,
) -> None:
    """Map the AC mode and compressor frequency to the hvac action."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            "power": power,
            "mode": mode,
            ACAttributes.compressor_frequency: frequency,
            ACAttributes.defrosting: False,
        },
    )
    assert entity.hvac_action == expected


@pytest.mark.parametrize(
    ("version", "expected_heat", "expected_fan"),
    [
        ((2024, 7), HVACAction.HEATING, HVACAction.FAN),
        ((2024, 8), "defrosting", "defrosting"),
    ],
)
def test_ac_hvac_action_defrosting(
    monkeypatch: pytest.MonkeyPatch,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
    version: tuple[int, int],
    expected_heat: str,
    expected_fan: str,
) -> None:
    """Report defrosting before the mode, only where HA has the action."""
    monkeypatch.setattr(climate_module, "MAJOR_VERSION", version[0])
    monkeypatch.setattr(climate_module, "MINOR_VERSION", version[1])
    # HVACAction.DEFROSTING is missing before HA 2024.8 (oldest test baseline)
    actions = {action.name: action for action in HVACAction}
    actions.setdefault("DEFROSTING", "defrosting")
    monkeypatch.setattr(climate_module, "HVACAction", SimpleNamespace(**actions))
    entity, _, values = make_ac(
        device_factory,
        install_config,
        attributes={
            "power": True,
            "mode": 4,
            ACAttributes.compressor_frequency: 50,
            ACAttributes.defrosting: True,
        },
    )
    assert entity.hvac_action == expected_heat
    values["mode"] = 5
    assert entity.hvac_action == expected_fan


@pytest.mark.parametrize(
    ("vertical", "horizontal", "expected"),
    [
        (False, False, SWING_OFF),
        (True, False, SWING_VERTICAL),
        (False, True, SWING_HORIZONTAL),
        (True, True, SWING_BOTH),
    ],
)
def test_ac_swing_state(
    vertical: bool,
    horizontal: bool,
    expected: str,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map both raw AC swing flags."""
    entity, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={
            ACAttributes.swing_vertical: vertical,
            ACAttributes.swing_horizontal: horizontal,
        },
    )
    assert entity.swing_mode == expected


@pytest.mark.parametrize("raw", [0, 0xFF, "invalid", None])
def test_ac_invalid_or_disabled_humidity(
    raw: object,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Suppress disabled, missing, and sentinel humidity values."""
    disabled, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={"indoor_humidity": 50},
    )
    assert disabled.current_humidity is None
    enabled, _, _ = make_ac(
        device_factory,
        install_config,
        attributes={"indoor_humidity": raw},
        sensors=["indoor_humidity"],
    )
    assert enabled.current_humidity is None


def test_cc_climate(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map CC fan, precision, and swing state and commands."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.CC)
    device, values = device_factory(
        device_type=DeviceType.CC,
        attributes={
            CCAttributes.fan_speed: FAN_LOW,
            CCAttributes.temperature_precision: 0.5,
            CCAttributes.swing: True,
        },
    )
    device.fan_modes = [FAN_LOW, FAN_HIGH]
    entity = MideaCCClimate(device, "main")
    assert entity.fan_modes == [FAN_LOW, FAN_HIGH]
    assert entity.fan_mode == FAN_LOW
    assert entity.target_temperature_step == pytest.approx(0.5)
    assert entity.swing_mode == SWING_ON
    values[CCAttributes.swing] = False
    assert entity.swing_mode == SWING_OFF
    entity.set_fan_mode(FAN_HIGH)
    entity.set_swing_mode(SWING_ON)
    entity.set_swing_mode(SWING_OFF)
    assert device.set_attribute.call_args_list == [
        call(attr=CCAttributes.fan_speed, value=FAN_HIGH),
        call(attr=CCAttributes.swing, value=True),
        call(attr=CCAttributes.swing, value=False),
    ]


def test_cf_climate(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Expose CF limits, range, temperature, and reduced features."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.CF)
    device, _ = device_factory(
        device_type=DeviceType.CF,
        attributes={
            CFAttributes.min_temperature: 5,
            CFAttributes.max_temperature: 35,
            CFAttributes.current_temperature: 20,
        },
    )
    entity = MideaCFClimate(device, "main")
    assert entity.supported_features == TARGET_AND_POWER_FEATURES
    assert entity.min_temp == 5
    assert entity.max_temp == 35
    assert entity.native_target_temperature_low == 5
    assert entity.native_target_temperature_high == 35
    assert entity.native_current_temperature == 20


@pytest.mark.parametrize("zone", [0, 1])
def test_c3_climate(
    zone: int,
    caplog: pytest.LogCaptureFixture,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map each C3 zone independently and dispatch zone-aware commands."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C3)
    attributes = {
        C3Attributes.zone1_power: True,
        C3Attributes.zone2_power: True,
        C3Attributes.mode: 2,
        C3Attributes.zone_temp_type: [True, False],
        C3Attributes.temperature_min: [10, 11],
        C3Attributes.temperature_max: [30, 31],
        C3Attributes.target_temperature: [20, 21],
    }
    device, values = device_factory(device_type=DeviceType.C3, attributes=attributes)
    entity = MideaC3Climate(device, "main", zone)
    expected_power_attr = (
        C3Attributes.zone1_power,
        C3Attributes.zone2_power,
    )[zone]
    assert entity.supported_features == TARGET_AND_POWER_FEATURES
    assert entity.target_temperature_step == (
        PRECISION_WHOLE if zone == 0 else PRECISION_HALVES
    )
    assert entity.min_temp == 10 + zone
    assert entity.max_temp == 30 + zone
    assert entity.native_target_temperature_low == 10 + zone
    assert entity.native_target_temperature_high == 30 + zone
    assert entity.hvac_mode is HVACMode.COOL
    assert entity.native_target_temperature == 20 + zone
    assert entity.native_current_temperature is None
    values[C3Attributes.mode] = -1
    assert entity.hvac_mode is HVACMode.OFF
    values[C3Attributes.mode] = "invalid"
    assert entity.hvac_mode is HVACMode.OFF
    values[expected_power_attr] = False
    assert entity.hvac_mode is HVACMode.OFF
    values[expected_power_attr] = True

    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: 22.26})
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 23, ATTR_HVAC_MODE: HVACMode.HEAT},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 24, ATTR_HVAC_MODE: HVACMode.OFF},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 25, ATTR_HVAC_MODE: "invalid"},
    )
    entity.set_hvac_mode(HVACMode.HEAT)
    entity.set_hvac_mode(HVACMode.OFF)
    entity.turn_on()
    entity.turn_off()
    assert device.set_target_temperature.call_args_list == [
        call(target_temperature=22.5, mode=None, zone=zone),
        call(target_temperature=23.0, mode=3, zone=zone),
    ]
    device.set_mode.assert_called_once_with(zone, 3)
    assert device.set_attribute.call_args_list == [
        call(attr=expected_power_attr, value=False),
        call(attr=expected_power_attr, value=False),
        call(attr=expected_power_attr, value=True),
        call(attr=expected_power_attr, value=False),
    ]
    assert "Error setting temperature" in caplog.text


def test_c1_state_and_commands(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map C1 boiler state, presets, temperatures, and power behavior."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C1)
    device, values = device_factory(
        device_type=DeviceType.C1,
        attributes={
            C1Attributes.power: True,
            C1Attributes.heating_mode: "unknown",
            C1Attributes.current_temperature: 21,
            C1Attributes.heating_target_temperature: 45,
        },
    )
    device.heating_modes = ["user", "activity", "sleep"]
    entity = MideaC1Climate(device, "main")
    expected_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    assert entity.supported_features == expected_features
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.preset_mode == "user"
    assert entity.native_current_temperature == pytest.approx(21.0)
    assert entity.native_target_temperature == pytest.approx(45.0)
    values[C1Attributes.power] = False
    assert entity.hvac_mode is HVACMode.OFF
    values[C1Attributes.heating_mode] = "sleep"
    assert entity.preset_mode == "sleep"
    values[C1Attributes.current_temperature] = "invalid"
    assert entity.native_current_temperature is None
    values[C1Attributes.heating_target_temperature] = None
    assert entity.native_target_temperature == pytest.approx(30.0)

    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: 42.6})
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 44, ATTR_HVAC_MODE: HVACMode.HEAT},
    )
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 46, ATTR_HVAC_MODE: HVACMode.OFF},
    )
    entity.set_hvac_mode(HVACMode.HEAT)
    entity.set_hvac_mode(HVACMode.OFF)
    assert device.set_attribute.call_args_list == [
        call(attr=C1Attributes.heating_target_temperature, value=43.0),
        call(attr="power", value=True),
        call(attr=C1Attributes.heating_target_temperature, value=44.0),
        call(attr="power", value=False),
        call(attr="power", value=True),
        call(attr="power", value=False),
    ]


@pytest.mark.parametrize(
    ("preset", "mode_code", "attribute"),
    [
        ("user", 1, C1Attributes.user_mode_target_temperature),
        ("activity", 2, C1Attributes.activity_mode_target_temperature),
        ("sleep", 3, C1Attributes.sleep_mode_target_temperature),
    ],
)
def test_c1_preset_with_per_mode_temperature(
    preset: str,
    mode_code: int,
    attribute: C1Attributes,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Switch C1 presets with their own cached target setpoint."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C1)
    device, _ = device_factory(
        device_type=DeviceType.C1,
        attributes={attribute: 48},
    )
    device.heating_modes = ["user", "activity", "sleep"]
    MideaC1Climate(device, "main").set_preset_mode(preset)
    device.set_heating_target_temperature.assert_called_once_with(
        48.0,
        heating_mode=mode_code,
    )


def test_c1_preset_fallbacks(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Fall back to the plain C1 mode command without a numeric setpoint."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C1)
    device, _ = device_factory(
        device_type=DeviceType.C1,
        attributes={
            C1Attributes.heating_mode: "unknown",
            C1Attributes.user_mode_target_temperature: "invalid",
        },
    )
    device.heating_modes = []
    entity = MideaC1Climate(device, "main")
    assert entity.preset_mode == "unknown"
    entity.set_preset_mode("user")
    entity.set_preset_mode("holiday")
    assert device.set_attribute.call_args_list == [
        call(attr=C1Attributes.heating_mode, value="user"),
        call(attr=C1Attributes.heating_mode, value="holiday"),
    ]


def test_pre_2024_2_feature_flags(
    monkeypatch: pytest.MonkeyPatch,
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Keep turn-on/off flags disabled for legacy HA feature contracts."""
    monkeypatch.setattr(climate_module, "MAJOR_VERSION", 2024)
    monkeypatch.setattr(climate_module, "MINOR_VERSION", 1)

    install_config({"main": {"type": Platform.CLIMATE}})
    base_device, _ = device_factory()
    base = MideaClimate(base_device, "main")
    assert base.supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.SWING_MODE
    )

    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.ED)
    tea_device, _ = device_factory(device_type=DeviceType.ED)
    assert MideaEDTeaBarClimate(tea_device, "main").supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )

    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.CF)
    cf_device, _ = device_factory(device_type=DeviceType.CF)
    assert MideaCFClimate(cf_device, "main").supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )

    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C3)
    c3_device, _ = device_factory(device_type=DeviceType.C3)
    assert MideaC3Climate(c3_device, "main", 0).supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )

    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.C1)
    c1_device, _ = device_factory(device_type=DeviceType.C1)
    c1_device.heating_modes = []
    assert MideaC1Climate(c1_device, "main").supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )

    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.FB)
    fb_device, _ = device_factory(device_type=DeviceType.FB)
    fb_device.modes = []
    assert MideaFBClimate(fb_device, "main").supported_features == (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )


def test_fb_climate(
    device_factory: DeviceFactory,
    install_config: InstallConfig,
) -> None:
    """Map FB state, commands, and reduced features."""
    install_config({"main": {"type": Platform.CLIMATE}}, DeviceType.FB)
    device, values = device_factory(
        device_type=DeviceType.FB,
        attributes={
            FBAttributes.mode: "manual",
            FBAttributes.power: True,
            FBAttributes.current_temperature: 18,
        },
    )
    device.modes = ["manual", "eco"]
    entity = MideaFBClimate(device, "main")
    expected_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    assert entity.supported_features == expected_features
    assert entity.preset_mode == "manual"
    assert entity.hvac_mode is HVACMode.HEAT
    assert entity.native_current_temperature == 18
    values[FBAttributes.power] = False
    assert entity.hvac_mode is HVACMode.OFF
    entity.set_temperature()
    entity.set_temperature(**{ATTR_TEMPERATURE: 20.26})
    entity.set_temperature(
        **{ATTR_TEMPERATURE: 21, ATTR_HVAC_MODE: HVACMode.OFF},
    )
    entity.set_hvac_mode(HVACMode.HEAT)
    entity.set_hvac_mode(HVACMode.OFF)
    entity.set_preset_mode("eco")
    device.set_target_temperature.assert_called_once_with(
        target_temperature=20.5,
        mode=None,
    )
    assert device.set_attribute.call_args_list == [
        call(attr="power", value=False),
        call(attr="power", value=True),
        call(attr="power", value=False),
        call(attr=FBAttributes.mode, value="eco"),
    ]
