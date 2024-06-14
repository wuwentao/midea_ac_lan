from homeassistant.const import Platform

DOMAIN = "midea_lan"
OLD_DOMAIN = "midea_ac_lan"
COMPONENT = "component"
DEVICES = "devices"
CONF_KEY = "key"
CONF_MODEL = "model"
CONF_SUBTYPE = "subtype"
CONF_ACCOUNT = "account"
CONF_SERVER = "server"
CONF_REFRESH_INTERVAL = "refresh_interval"
EXTRA_SENSOR = [Platform.SENSOR, Platform.BINARY_SENSOR]
EXTRA_SWITCH = [Platform.SWITCH, Platform.LOCK, Platform.SELECT, Platform.NUMBER]
EXTRA_CONTROL = [
    Platform.CLIMATE,
    Platform.WATER_HEATER,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.LIGHT,
] + EXTRA_SWITCH
ALL_PLATFORM = EXTRA_SENSOR + EXTRA_CONTROL
