import logging

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_SWITCHES, Platform

from .const import DEVICES, DOMAIN
from .midea_devices import MIDEA_DEVICES
from .midea_entity import MideaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    device_id = config_entry.data.get(CONF_DEVICE_ID)
    device = hass.data[DOMAIN][DEVICES].get(device_id)
    extra_switches = config_entry.options.get(CONF_SWITCHES, [])
    devs = []
    for entity_key, config in MIDEA_DEVICES[device.device_type]["entities"].items():
        if config["type"] == Platform.HUMIDIFIER and (
            config.get("default") or entity_key in extra_switches
        ):
            if device.device_type == 0xA1:
                devs.append(MideaA1Humidifier(device, entity_key))
            if device.device_type == 0xFD:
                devs.append(MideaFDHumidifier(device, entity_key))
    async_add_entities(devs)


class MideaHumidifier(MideaEntity, HumidifierEntity):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)

    @property
    def target_humidity(self):
        return self._device.get_attribute("target_humidity")

    @property
    def mode(self):
        return self._device.get_attribute("mode")

    @property
    def available_modes(self):
        return self._device.modes

    def set_humidity(self, humidity: int):
        self._device.set_attribute("target_humidity", humidity)

    def set_mode(self, mode: str):
        self._device.set_attribute("mode", mode)

    @property
    def min_humidity(self):
        return self._min_humidity

    @property
    def max_humidity(self):
        return self._max_humidity

    @property
    def is_on(self):
        return self._device.get_attribute(attr="power")

    def turn_on(self):
        self._device.set_attribute(attr="power", value=True)

    def turn_off(self):
        self._device.set_attribute(attr="power", value=False)

    def update_state(self, status):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(
                f"Entity {self.entity_id} update_state {repr(e)}, status = {status}"
            )


class MideaA1Humidifier(MideaHumidifier):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._min_humidity = 35
        self._max_humidity = 85

    @property
    def device_class(self):
        return HumidifierDeviceClass.DEHUMIDIFIER

    @property
    def supported_features(self):
        return HumidifierEntityFeature.MODES


class MideaFDHumidifier(MideaHumidifier):
    def __init__(self, device, entity_key):
        super().__init__(device, entity_key)
        self._min_humidity = 35
        self._max_humidity = 85

    @property
    def device_class(self):
        return HumidifierDeviceClass.HUMIDIFIER

    @property
    def supported_features(self):
        return HumidifierEntityFeature.MODES
