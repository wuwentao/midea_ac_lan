import logging
from typing import Any, TypeAlias, cast

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
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
    MAJOR_VERSION,
    MINOR_VERSION,
    PRECISION_HALVES,
    PRECISION_WHOLE,
    Platform,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.ac import MideaACDevice
from midealocal.devices.c3 import DeviceAttributes as C3Attributes
from midealocal.devices.c3 import MideaC3Device
from midealocal.devices.cc import DeviceAttributes as CCAttributes
from midealocal.devices.cc import MideaCCDevice
from midealocal.devices.cf import DeviceAttributes as CFAttributes
from midealocal.devices.cf import MideaCFDevice
from midealocal.devices.fb import DeviceAttributes as FBAttributes
from midealocal.devices.fb import MideaFBDevice

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


TEMPERATURE_MAX = 30
TEMPERATURE_MIN = 17

FAN_SILENT = "silent"
FAN_FULL_SPEED = "full"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs: list[
        MideaACClimate
        | MideaCCClimate
        | MideaCFClimate
        | MideaC3Climate
        | MideaFBClimate
    ] = []
    for entity_key, config in cast(
        dict,
        MIDEA_DEVICES[device.device_type]["entities"],
    ).items():
        if config["type"] == Platform.CLIMATE and (
            config.get("default") or entity_key in extra_switches
        ):
            if device.device_type == 0xAC:
                devs.append(MideaACClimate(device, entity_key))
            elif device.device_type == 0xCC:
                devs.append(MideaCCClimate(device, entity_key))
            elif device.device_type == 0xCF:
                devs.append(MideaCFClimate(device, entity_key))
            elif device.device_type == 0xC3:
                devs.append(MideaC3Climate(device, entity_key, config["zone"]))
            elif device.device_type == 0xFB:
                devs.append(MideaFBClimate(device, entity_key))
    async_add_entities(devs)


MideaClimateDevice: TypeAlias = (
    MideaACDevice | MideaCCDevice | MideaCFDevice | MideaC3Device | MideaFBDevice
)


class MideaClimate(MideaEntity, ClimateEntity):
    # https://developers.home-assistant.io/blog/2024/01/24/climate-climateentityfeatures-expanded
    _enable_turn_on_off_backwards_compatibility: bool = (
        False  # maybe remove after 2025.1
    )

    _device: MideaClimateDevice

    _attr_max_temp: float = TEMPERATURE_MAX
    _attr_min_temp: float = TEMPERATURE_MIN
    _attr_target_temperature_high: float | None = TEMPERATURE_MAX
    _attr_target_temperature_low: float | None = TEMPERATURE_MIN
    _attr_temperature_unit: str = UnitOfTemperature.CELSIUS

    def __init__(self, device: MideaClimateDevice, entity_key: str) -> None:
        super().__init__(device, entity_key)

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.SWING_MODE
        )
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def hvac_mode(self) -> HVACMode:
        if self._device.get_attribute("power"):
            return cast(HVACMode, self.hvac_modes[self._device.get_attribute("mode")])
        else:
            return HVACMode.OFF

    @property
    def target_temperature(self) -> float:
        return cast(float, self._device.get_attribute("target_temperature"))

    @property
    def current_temperature(self) -> float | None:
        return cast(float | None, self._device.get_attribute("indoor_temperature"))

    @property
    def preset_mode(self) -> str:
        if self._device.get_attribute("comfort_mode"):
            mode = PRESET_COMFORT
        elif self._device.get_attribute("eco_mode"):
            mode = PRESET_ECO
        elif self._device.get_attribute("boost_mode"):
            mode = PRESET_BOOST
        elif self._device.get_attribute("sleep_mode"):
            mode = PRESET_SLEEP
        elif self._device.get_attribute("frost_protect"):
            mode = PRESET_AWAY
        else:
            mode = PRESET_NONE
        return mode

    @property
    def extra_state_attributes(self) -> dict:
        return cast(dict, self._device.attributes)

    def turn_on(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr="power", value=False)

    def set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs[ATTR_TEMPERATURE]) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            try:
                mode = self.hvac_modes.index(hvac_mode.lower()) if hvac_mode else None
                self._device.set_target_temperature(
                    target_temperature=temperature,
                    mode=mode,
                )
            except ValueError as e:
                _LOGGER.error("set_temperature %s, kwargs = %s", e, kwargs)

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_attribute(
                attr="mode", value=self.hvac_modes.index(hvac_mode)
            )

    def set_preset_mode(self, preset_mode: str) -> None:
        old_mode = self.preset_mode
        preset_mode = preset_mode.lower()
        if preset_mode == PRESET_AWAY:
            self._device.set_attribute(attr="frost_protect", value=True)
        elif preset_mode == PRESET_COMFORT:
            self._device.set_attribute(attr="comfort_mode", value=True)
        elif preset_mode == PRESET_SLEEP:
            self._device.set_attribute(attr="sleep_mode", value=True)
        elif preset_mode == PRESET_ECO:
            self._device.set_attribute(attr="eco_mode", value=True)
        elif preset_mode == PRESET_BOOST:
            self._device.set_attribute(attr="boost_mode", value=True)
        elif old_mode == PRESET_AWAY:
            self._device.set_attribute(attr="frost_protect", value=False)
        elif old_mode == PRESET_COMFORT:
            self._device.set_attribute(attr="comfort_mode", value=False)
        elif old_mode == PRESET_SLEEP:
            self._device.set_attribute(attr="sleep_mode", value=False)
        elif old_mode == PRESET_ECO:
            self._device.set_attribute(attr="eco_mode", value=False)
        elif old_mode == PRESET_BOOST:
            self._device.set_attribute(attr="boost_mode", value=False)

    def update_state(self, status: Any) -> None:
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(
                "Entity %s update_state %s, status = %s",
                self.entity_id,
                repr(e),
                status,
            )


class MideaACClimate(MideaClimate):
    _device: MideaACDevice

    def __init__(self, device: MideaACDevice, entity_key: str) -> None:
        super().__init__(device, entity_key)
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
            HVACMode.DRY,
            HVACMode.HEAT,
            HVACMode.FAN_ONLY,
        ]
        self._fan_speeds: dict[str, int] = {
            FAN_SILENT: 20,
            FAN_LOW: 40,
            FAN_MEDIUM: 60,
            FAN_HIGH: 80,
            FAN_FULL_SPEED: 100,
            FAN_AUTO: 102,
        }
        self._attr_swing_modes: list[str] = [
            SWING_OFF,
            SWING_VERTICAL,
            SWING_HORIZONTAL,
            SWING_BOTH,
        ]
        self._attr_preset_modes = [
            PRESET_NONE,
            PRESET_COMFORT,
            PRESET_ECO,
            PRESET_BOOST,
            PRESET_SLEEP,
            PRESET_AWAY,
        ]

        self._attr_fan_modes = list(self._fan_speeds.keys())

    @property
    def fan_mode(self) -> str:
        fan_speed: int = self._device.get_attribute(ACAttributes.fan_speed)
        if fan_speed > 100:
            return FAN_AUTO
        elif fan_speed > 80:
            return FAN_FULL_SPEED
        elif fan_speed > 60:
            return FAN_HIGH
        elif fan_speed > 40:
            return FAN_MEDIUM
        elif fan_speed > 20:
            return FAN_LOW
        else:
            return FAN_SILENT

    @property
    def target_temperature_step(self) -> float:
        return (
            PRECISION_WHOLE if self._device.temperature_step == 1 else PRECISION_HALVES
        )

    @property
    def swing_mode(self) -> str:
        swing_mode = (
            1 if self._device.get_attribute(ACAttributes.swing_vertical) else 0
        ) + (2 if self._device.get_attribute(ACAttributes.swing_horizontal) else 0)
        return self._attr_swing_modes[swing_mode]

    @property
    def outdoor_temperature(self) -> float:
        return cast(float, self._device.get_attribute(ACAttributes.outdoor_temperature))

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds.get(fan_mode)
        if fan_speed:
            self._device.set_attribute(attr=ACAttributes.fan_speed, value=fan_speed)

    def set_swing_mode(self, swing_mode: str) -> None:
        swing = self._attr_swing_modes.index(swing_mode)
        swing_vertical = swing & 1 > 0
        swing_horizontal = swing & 2 > 0
        self._device.set_swing(
            swing_vertical=swing_vertical,
            swing_horizontal=swing_horizontal,
        )


class MideaCCClimate(MideaClimate):
    _device: MideaCCDevice

    def __init__(self, device: MideaCCDevice, entity_key: str) -> None:
        super().__init__(device, entity_key)
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.FAN_ONLY,
            HVACMode.DRY,
            HVACMode.HEAT,
            HVACMode.COOL,
            HVACMode.AUTO,
        ]
        self._attr_swing_modes = [SWING_OFF, SWING_ON]
        self._attr_preset_modes = [PRESET_NONE, PRESET_SLEEP, PRESET_ECO]

    @property
    def fan_modes(self) -> list[str] | None:
        return cast(list, self._device.fan_modes)

    @property
    def fan_mode(self) -> str:
        return cast(str, self._device.get_attribute(CCAttributes.fan_speed))

    @property
    def target_temperature_step(self) -> float:
        return cast(
            float,
            self._device.get_attribute(CCAttributes.temperature_precision),
        )

    @property
    def swing_mode(self) -> str:
        return SWING_ON if self._device.get_attribute(CCAttributes.swing) else SWING_OFF

    def set_fan_mode(self, fan_mode: str) -> None:
        self._device.set_attribute(attr=CCAttributes.fan_speed, value=fan_mode)

    def set_swing_mode(self, swing_mode: str) -> None:
        self._device.set_attribute(
            attr=CCAttributes.swing,
            value=swing_mode == SWING_ON,
        )


class MideaCFClimate(MideaClimate):
    _device: MideaCFDevice

    _attr_target_temperature_step: float | None = PRECISION_WHOLE

    def __init__(self, device: MideaCFDevice, entity_key: str) -> None:
        super().__init__(device, entity_key)
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
            HVACMode.HEAT,
        ]

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def min_temp(self) -> float:
        return cast(float, self._device.get_attribute(CFAttributes.min_temperature))

    @property
    def max_temp(self) -> float:
        return cast(float, self._device.get_attribute(CFAttributes.max_temperature))

    @property
    def target_temperature_low(self) -> float:
        return cast(float, self._device.get_attribute(CFAttributes.min_temperature))

    @property
    def target_temperature_high(self) -> float:
        return cast(float, self._device.get_attribute(CFAttributes.max_temperature))

    @property
    def current_temperature(self) -> float:
        return cast(float, self._device.get_attribute(CFAttributes.current_temperature))


class MideaC3Climate(MideaClimate):
    _device: MideaC3Device

    _powers = [
        C3Attributes.zone1_power,
        C3Attributes.zone2_power,
    ]

    def __init__(self, device: MideaC3Device, entity_key: str, zone: int) -> None:
        super().__init__(device, entity_key)
        self._zone = zone
        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.AUTO,
            HVACMode.COOL,
            HVACMode.HEAT,
        ]
        self._power_attr = MideaC3Climate._powers[zone]

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def target_temperature_step(self) -> float:
        return (
            PRECISION_WHOLE
            if self._device.get_attribute(C3Attributes.zone_temp_type)[self._zone]
            else PRECISION_HALVES
        )

    @property
    def min_temp(self) -> float:
        return cast(
            float,
            self._device.get_attribute(C3Attributes.temperature_min)[self._zone],
        )

    @property
    def max_temp(self) -> float:
        return cast(
            float,
            self._device.get_attribute(C3Attributes.temperature_max)[self._zone],
        )

    @property
    def target_temperature_low(self) -> float:
        return cast(
            float,
            self._device.get_attribute(C3Attributes.temperature_min)[self._zone],
        )

    @property
    def target_temperature_high(self) -> float:
        return cast(
            float,
            self._device.get_attribute(C3Attributes.temperature_max)[self._zone],
        )

    def turn_on(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr=self._power_attr, value=True)

    def turn_off(self, **kwargs: Any) -> None:
        self._device.set_attribute(attr=self._power_attr, value=False)

    @property
    def hvac_mode(self) -> HVACMode:
        if self._device.get_attribute(self._power_attr):
            return cast(
                HVACMode,
                self._modes[self._device.get_attribute(C3Attributes.mode)],
            )
        else:
            return HVACMode.OFF

    @property
    def target_temperature(self) -> float:
        return cast(
            float,
            self._device.get_attribute(C3Attributes.target_temperature)[self._zone],
        )

    @property
    def current_temperature(self) -> float | None:
        return None

    def set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs[ATTR_TEMPERATURE]) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            try:
                mode = self.hvac_modes.index(hvac_mode.lower()) if hvac_mode else None
                self._device.set_target_temperature(
                    zone=self._zone,
                    target_temperature=temperature,
                    mode=mode,
                )
            except ValueError as e:
                _LOGGER.error("set_temperature %s, kwargs = %s", e, kwargs)

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_mode(self._zone, self.hvac_modes.index(hvac_mode))


class MideaFBClimate(MideaClimate):
    _device: MideaFBDevice

    _attr_max_temp: float = 35
    _attr_min_temp: float = 5
    _attr_target_temperature_high: float | None = 35
    _attr_target_temperature_low: float | None = 5
    _attr_target_temperature_step: float | None = PRECISION_WHOLE

    def __init__(self, device: MideaFBDevice, entity_key: str) -> None:
        super().__init__(device, entity_key)
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_preset_modes: list[str] = self._device.modes

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def preset_mode(self) -> str:
        return cast(str, self._device.get_attribute(attr=FBAttributes.mode))

    @property
    def hvac_mode(self) -> HVACMode:
        return (
            HVACMode.HEAT
            if self._device.get_attribute(attr=FBAttributes.power)
            else HVACMode.OFF
        )

    @property
    def current_temperature(self) -> float:
        return cast(float, self._device.get_attribute(FBAttributes.current_temperature))

    def set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs[ATTR_TEMPERATURE]) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_attribute(
                attr=FBAttributes.target_temperature,
                value=temperature,
            )

    def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self.turn_on()

    def set_preset_mode(self, preset_mode: str) -> None:
        self._device.set_attribute(attr=FBAttributes.mode, value=preset_mode)
