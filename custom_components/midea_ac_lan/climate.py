from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ClimateEntity,
    ClimateEntityFeature,
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    HVACMode,
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
)
from homeassistant.const import (
    MAJOR_VERSION,
    MINOR_VERSION,
    Platform,
    UnitOfTemperature,
    PRECISION_WHOLE,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
)

from .const import (
    DOMAIN,
    DEVICES,
)
from .midea.devices.ac.device import DeviceAttributes as ACAttributes
from .midea.devices.c3.device import DeviceAttributes as C3Attributes
from .midea.devices.cc.device import DeviceAttributes as CCAttributes
from .midea.devices.cf.device import DeviceAttributes as CFAttributes
from .midea.devices.fb.device import DeviceAttributes as FBAttributes
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

import logging
_LOGGER = logging.getLogger(__name__)


TEMPERATURE_MAX = 30
TEMPERATURE_MIN = 17

FAN_SILENT = "Silent"
FAN_FULL_SPEED = "Full"


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.CLIMATE and (config.get("default") or entity_key in extra_switches):
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


class MideaClimate(MideaEntity, ClimateEntity):

    # https://developers.home-assistant.io/blog/2024/01/24/climate-climateentityfeatures-expanded
    _enable_turn_on_off_backwards_compatibility: bool = False  # maybe remove after 2025.1

    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def supported_features(self):
        features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.FAN_MODE |
            ClimateEntityFeature.PRESET_MODE |
            ClimateEntityFeature.SWING_MODE
        )
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def min_temp(self):
        return TEMPERATURE_MIN

    @property
    def max_temp(self):
        return TEMPERATURE_MAX

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def target_temperature_low(self):
        return TEMPERATURE_MIN

    @property
    def target_temperature_high(self):
        return TEMPERATURE_MAX

    @property
    def hvac_modes(self):
        return self._modes

    @property
    def swing_modes(self):
        return self._swing_modes

    @property
    def is_on(self) -> bool:
        return self.hvac_mode != HVACMode.OFF

    @property
    def hvac_mode(self) -> str:
        if self._device.get_attribute("power"):
            return self._modes[self._device.get_attribute("mode")]
        else:
            return HVACMode.OFF

    @property
    def target_temperature(self):
        return self._device.get_attribute("target_temperature")

    @property
    def current_temperature(self):
        return self._device.get_attribute("indoor_temperature")

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
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
        return self._device.attributes

    def turn_on(self):
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    def set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs.get(ATTR_TEMPERATURE)) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            try:
                mode = self._modes.index(hvac_mode.lower()) if hvac_mode else None
                self._device.set_target_temperature(
                    target_temperature=temperature, mode=mode)
            except ValueError as e:
                _LOGGER.error(f"set_temperature {e}, kwargs = {kwargs}")

    def set_hvac_mode(self, hvac_mode: str) -> None:
        hvac_mode = hvac_mode.lower()
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_attribute(attr="mode", value=self._modes.index(hvac_mode))

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

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(f"Entity {self.entity_id} update_state {repr(e)}, status = {status}")


class MideaACClimate(MideaClimate):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.DRY, HVACMode.HEAT, HVACMode.FAN_ONLY]
        self._fan_speeds = {
            FAN_SILENT.capitalize(): 20,
            FAN_LOW.capitalize(): 40,
            FAN_MEDIUM.capitalize(): 60,
            FAN_HIGH.capitalize(): 80,
            FAN_FULL_SPEED.capitalize(): 100,
            FAN_AUTO.capitalize(): 102
        }
        self._swing_modes = [
            SWING_OFF.capitalize(),
            SWING_VERTICAL.capitalize(),
            SWING_HORIZONTAL.capitalize(),
            SWING_BOTH.capitalize()
        ]
        self._preset_modes = [PRESET_NONE, PRESET_COMFORT, PRESET_ECO, PRESET_BOOST, PRESET_SLEEP, PRESET_AWAY]

    @property
    def fan_modes(self):
        return list(self._fan_speeds.keys())

    @property
    def fan_mode(self) -> str:
        fan_speed = self._device.get_attribute(ACAttributes.fan_speed)
        if fan_speed > 100:
            return FAN_AUTO.capitalize()
        elif fan_speed > 80:
            return FAN_FULL_SPEED.capitalize()
        elif fan_speed > 60:
            return FAN_HIGH.capitalize()
        elif fan_speed > 40:
            return FAN_MEDIUM.capitalize()
        elif fan_speed > 20:
            return FAN_LOW.capitalize()
        else:
            return FAN_SILENT.capitalize()

    @property
    def target_temperature_step(self):
        return PRECISION_WHOLE if self._device.temperature_step == 1 else PRECISION_HALVES

    @property
    def swing_mode(self):
        swing_mode = (1 if self._device.get_attribute(ACAttributes.swing_vertical) else 0) + \
                     (2 if self._device.get_attribute(ACAttributes.swing_horizontal) else 0)
        return self._swing_modes[swing_mode]

    @property
    def outdoor_temperature(self):
        return self._device.get_attribute(ACAttributes.outdoor_temperature)

    def set_fan_mode(self, fan_mode: str) -> None:
        fan_speed = self._fan_speeds.get(fan_mode.capitalize())
        if fan_speed:
            self._device.set_attribute(attr=ACAttributes.fan_speed, value=fan_speed)

    def set_swing_mode(self, swing_mode: str) -> None:
        swing = self._swing_modes.index(swing_mode.capitalize())
        swing_vertical = swing & 1 > 0
        swing_horizontal = swing & 2 > 0
        self._device.set_swing(swing_vertical=swing_vertical, swing_horizontal=swing_horizontal)


class MideaCCClimate(MideaClimate):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._modes = [HVACMode.OFF, HVACMode.FAN_ONLY, HVACMode.DRY, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
        self._swing_modes = [
            SWING_OFF.capitalize(),
            SWING_ON.capitalize()
        ]
        self._preset_modes = [PRESET_NONE, PRESET_SLEEP, PRESET_ECO]

    @property
    def fan_modes(self):
        return self._device.fan_modes

    @property
    def fan_mode(self) -> str:
        return self._device.get_attribute(CCAttributes.fan_speed)

    @property
    def target_temperature_step(self):
        return self._device.get_attribute(CCAttributes.temperature_precision)

    @property
    def swing_mode(self):
        return SWING_ON.capitalize() if self._device.get_attribute(CCAttributes.swing) else SWING_OFF.capitalize()

    def set_fan_mode(self, fan_mode: str) -> None:
        self._device.set_attribute(attr=CCAttributes.fan_speed, value=fan_mode)

    def set_swing_mode(self, swing_mode: str) -> None:
        self._device.set_attribute(
            attr=CCAttributes.swing,
            value=swing_mode.capitalize() == SWING_ON.capitalize()
        )


class MideaCFClimate(MideaClimate):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT]

    @property
    def supported_features(self):
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def target_temperature_step(self):
        return PRECISION_WHOLE

    @property
    def min_temp(self):
        return self._device.get_attribute(CFAttributes.min_temperature)

    @property
    def max_temp(self):
        return self._device.get_attribute(CFAttributes.max_temperature)

    @property
    def target_temperature_low(self):
        return self._device.get_attribute(CFAttributes.min_temperature)

    @property
    def target_temperature_high(self):
        return self._device.get_attribute(CFAttributes.max_temperature)

    @property
    def current_temperature(self):
        return self._device.get_attribute(CFAttributes.current_temperature)


class MideaC3Climate(MideaClimate):
    _powers = [
        C3Attributes.zone1_power,
        C3Attributes.zone2_power,
    ]

    def __init__(self, device, entity_key, zone):
        super().__init__(device, entity_key)
        self._zone = zone
        self._modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT]
        self._power_attr = MideaC3Climate._powers[self._zone]

    @property
    def supported_features(self):
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def target_temperature_step(self):
        return PRECISION_WHOLE if \
            self._device.get_attribute(C3Attributes.zone_temp_type)[self._zone] else PRECISION_HALVES

    @property
    def min_temp(self):
        return self._device.get_attribute(C3Attributes.temperature_min)[self._zone]

    @property
    def max_temp(self):
        return self._device.get_attribute(C3Attributes.temperature_max)[self._zone]

    @property
    def target_temperature_low(self):
        return self._device.get_attribute(C3Attributes.temperature_min)[self._zone]

    @property
    def target_temperature_high(self):
        return self._device.get_attribute(C3Attributes.temperature_max)[self._zone]

    def turn_on(self):
        self._device.set_attribute(attr=self._power_attr, value=True)

    def turn_off(self):
        self._device.set_attribute(attr=self._power_attr, value=False)

    @property
    def hvac_mode(self) -> str:
        if self._device.get_attribute(self._power_attr):
            return self._modes[self._device.get_attribute(C3Attributes.mode)]
        else:
            return HVACMode.OFF

    @property
    def target_temperature(self):
        return self._device.get_attribute(C3Attributes.target_temperature)[self._zone]

    @property
    def current_temperature(self):
        return None

    def set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs.get(ATTR_TEMPERATURE)) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            try:
                mode = self._modes.index(hvac_mode.lower()) if hvac_mode else None
                self._device.set_target_temperature(
                    zone=self._zone, target_temperature=temperature, mode=mode)
            except ValueError as e:
                _LOGGER.error(f"set_temperature {e}, kwargs = {kwargs}")

    def set_hvac_mode(self, hvac_mode: str) -> None:
        hvac_mode = hvac_mode.lower()
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_mode(self._zone, self._modes.index(hvac_mode))


class MideaFBClimate(MideaClimate):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._modes = [HVACMode.OFF, HVACMode.HEAT]
        self._preset_modes = self._device.modes

    @property
    def supported_features(self):
        features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        if (MAJOR_VERSION, MINOR_VERSION) >= (2024, 2):
            features |= ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON
        return features

    @property
    def target_temperature_step(self):
        return PRECISION_WHOLE

    @property
    def preset_modes(self):
        return self._preset_modes

    @property
    def preset_mode(self):
        return self._device.get_attribute(attr=FBAttributes.mode)

    @property
    def min_temp(self):
        return 5

    @property
    def max_temp(self):
        return 35

    @property
    def target_temperature_low(self):
        return 5

    @property
    def target_temperature_high(self):
        return 35

    @property
    def hvac_mode(self) -> str:
        return HVACMode.HEAT if self._device.get_attribute(attr=FBAttributes.power) else HVACMode.OFF

    @property
    def current_temperature(self):
        return self._device.get_attribute(FBAttributes.current_temperature)

    def set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = float(int((float(kwargs.get(ATTR_TEMPERATURE)) * 2) + 0.5)) / 2
        hvac_mode = kwargs.get(ATTR_HVAC_MODE)
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self._device.set_attribute(attr=FBAttributes.target_temperature, value=temperature)

    def set_hvac_mode(self, hvac_mode: str) -> None:
        hvac_mode = hvac_mode.lower()
        if hvac_mode == HVACMode.OFF:
            self.turn_off()
        else:
            self.turn_on()

    def set_preset_mode(self, preset_mode: str) -> None:
        self._device.set_attribute(attr=FBAttributes.mode,value=preset_mode)
