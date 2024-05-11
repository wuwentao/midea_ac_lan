import functools as ft

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import (
    Platform,
    UnitOfTemperature,
    PRECISION_WHOLE,
    PRECISION_HALVES,
    ATTR_TEMPERATURE,
    CONF_DEVICE_ID,
    CONF_SWITCHES,
    STATE_ON,
    STATE_OFF,
)
from .const import (
    DOMAIN,
    DEVICES
)
from .midea.devices.e6.device import DeviceAttributes as E6Attributes
from .midea.devices.c3.device import DeviceAttributes as C3Attributes
from .midea.devices.cd.device import DeviceAttributes as CDAttributes
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

import logging
_LOGGER = logging.getLogger(__name__)

E2_TEMPERATURE_MAX = 75
E2_TEMPERATURE_MIN = 30
E3_TEMPERATURE_MAX = 65
E3_TEMPERATURE_MIN = 35


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(
        CONF_SWITCHES, []
    )
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.WATER_HEATER and (config.get("default") or entity_key in extra_switches):
            if device.device_type == 0xE2:
                devs.append(MideaE2WaterHeater(device, entity_key))
            elif device.device_type == 0xE3:
                devs.append(MideaE3WaterHeater(device, entity_key))
            elif device.device_type == 0xE6:
                devs.append(MideaE6WaterHeater(device, entity_key, config["use"]))
            elif device.device_type == 0xC3:
                devs.append(MideaC3WaterHeater(device, entity_key))
            elif device.device_type == 0xCD:
                devs.append(MideaCDWaterHeater(device, entity_key))
    async_add_entities(devs)


class MideaWaterHeater(MideaEntity, WaterHeaterEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._operations = []

    @property
    def supported_features(self):
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE

    @property
    def extra_state_attributes(self) -> dict:
        attrs = self._device.attributes
        if hasattr(self._device, "temperature_step"):
            attrs["target_temp_step"] = self._device.temperature_step
        return attrs

    @property
    def min_temp(self):
        return NotImplementedError

    @property
    def max_temp(self):
        return NotImplementedError

    @property
    def target_temperature_low(self):
        return self.min_temp

    @property
    def target_temperature_high(self):
        return self.max_temp

    @property
    def precision(self):
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def current_operation(self):
        return self._device.get_attribute("mode") if self._device.get_attribute("power") else STATE_OFF

    @property
    def current_temperature(self):
        return self._device.get_attribute("current_temperature")

    @property
    def target_temperature(self):
        return self._device.get_attribute("target_temperature")

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute("target_temperature", temperature)

    def set_operation_mode(self, operation_mode):
        self._device.set_attribute(attr="mode", value=operation_mode)

    @property
    def operation_list(self):
        return getattr(self._device, "preset_modes")

    def turn_on(self):
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(ft.partial(self.turn_on, **kwargs))

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(ft.partial(self.turn_off, **kwargs))

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(f"Entity {self.entity_id} update_state {repr(e)}, status = {status}")


class MideaE2WaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def min_temp(self):
        return E2_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E2_TEMPERATURE_MAX


class MideaE3WaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def min_temp(self):
        return E3_TEMPERATURE_MIN

    @property
    def max_temp(self):
        return E3_TEMPERATURE_MAX

    @property
    def precision(self):
        return PRECISION_HALVES if self._device.precision_halves else PRECISION_WHOLE


class MideaC3WaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def state(self):
        return STATE_ON if self._device.get_attribute(C3Attributes.dhw_power) else STATE_OFF

    @property
    def current_temperature(self):
        return self._device.get_attribute(C3Attributes.tank_actual_temperature)

    @property
    def target_temperature(self):
        return self._device.get_attribute(C3Attributes.dhw_target_temp)

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute(C3Attributes.dhw_target_temp, temperature)

    @property
    def min_temp(self):
        return self._device.get_attribute(C3Attributes.dhw_temp_min)

    @property
    def max_temp(self):
        return self._device.get_attribute(C3Attributes.dhw_temp_max)

    def turn_on(self):
        self._device.set_attribute(attr=C3Attributes.dhw_power, value=True)

    def turn_off(self):
        self._device.set_attribute(attr=C3Attributes.dhw_power, value=False)


class MideaE6WaterHeater(MideaWaterHeater):
    _powers = [
        E6Attributes.heating_power,
        E6Attributes.main_power,
    ]
    _current_temperatures = [
        E6Attributes.heating_leaving_temperature,
        E6Attributes.bathing_leaving_temperature,
    ]
    _target_temperatures = [
        E6Attributes.heating_temperature,
        E6Attributes.bathing_temperature,
    ]

    def __init__(self, device, entity_key, use):
        super().__init__(device, entity_key)
        self._use = use
        self._power_attr = MideaE6WaterHeater._powers[self._use]
        self._current_temperature_attr = MideaE6WaterHeater._current_temperatures[self._use]
        self._target_temperature_attr = MideaE6WaterHeater._target_temperatures[self._use]

    @property
    def state(self):
        if self._use == 0:  # for heating
            return STATE_ON if \
                self._device.get_attribute(E6Attributes.main_power) and \
                self._device.get_attribute(E6Attributes.heating_power) \
                else STATE_OFF
        else:  # for bathing
            return STATE_ON if \
                self._device.get_attribute(E6Attributes.main_power) \
                else STATE_OFF

    @property
    def current_temperature(self):
        return self._device.get_attribute(self._current_temperature_attr)

    @property
    def target_temperature(self):
        return self._device.get_attribute(self._target_temperature_attr)

    def set_temperature(self, **kwargs):
        if ATTR_TEMPERATURE not in kwargs:
            return
        temperature = int(kwargs.get(ATTR_TEMPERATURE))
        self._device.set_attribute(self._target_temperature_attr, temperature)

    @property
    def min_temp(self):
        return self._device.get_attribute(E6Attributes.min_temperature)[self._use]

    @property
    def max_temp(self):
        return self._device.get_attribute(E6Attributes.max_temperature)[self._use]

    def turn_on(self):
        self._device.set_attribute(attr=self._power_attr, value=True)

    def turn_off(self):
        self._device.set_attribute(attr=self._power_attr, value=False)


class MideaCDWaterHeater(MideaWaterHeater):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def supported_features(self):
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE | \
               WaterHeaterEntityFeature.OPERATION_MODE

    @property
    def min_temp(self):
        return self._device.get_attribute(CDAttributes.min_temperature)

    @property
    def max_temp(self):
        return self._device.get_attribute(CDAttributes.max_temperature)
