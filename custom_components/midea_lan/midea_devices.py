"""Devices configuration for Midea Lan."""

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    Platform,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolume,
)
from midealocal.devices.a1 import DeviceAttributes as A1Attributes
from midealocal.devices.ac import DeviceAttributes as ACAttributes
from midealocal.devices.b0 import DeviceAttributes as B0Attributes
from midealocal.devices.b1 import DeviceAttributes as B1Attributes
from midealocal.devices.b3 import DeviceAttributes as B3Attributes
from midealocal.devices.b4 import DeviceAttributes as B4Attributes
from midealocal.devices.b6 import DeviceAttributes as B6Attributes
from midealocal.devices.bf import DeviceAttributes as BFAttributes
from midealocal.devices.c2 import DeviceAttributes as C2Attributes
from midealocal.devices.c3 import DeviceAttributes as C3Attributes
from midealocal.devices.ca import DeviceAttributes as CAAttributes
from midealocal.devices.cc import DeviceAttributes as CCAttributes
from midealocal.devices.cd import DeviceAttributes as CDAttributes
from midealocal.devices.ce import DeviceAttributes as CEAttributes
from midealocal.devices.cf import DeviceAttributes as CFAttributes
from midealocal.devices.da import DeviceAttributes as DAAttributes
from midealocal.devices.db import DeviceAttributes as DBAttributes
from midealocal.devices.dc import DeviceAttributes as DCAttributes
from midealocal.devices.e1 import DeviceAttributes as E1Attributes
from midealocal.devices.e2 import DeviceAttributes as E2Attributes
from midealocal.devices.e3 import DeviceAttributes as E3Attributes
from midealocal.devices.e6 import DeviceAttributes as E6Attributes
from midealocal.devices.e8 import DeviceAttributes as E8Attributes
from midealocal.devices.ea import DeviceAttributes as EAAttributes
from midealocal.devices.ec import DeviceAttributes as ECAttributes
from midealocal.devices.ed import DeviceAttributes as EDAttributes
from midealocal.devices.fa import DeviceAttributes as FAAttributes
from midealocal.devices.fb import DeviceAttributes as FBAttributes
from midealocal.devices.fc import DeviceAttributes as FCAttributes
from midealocal.devices.fd import DeviceAttributes as FDAttributes
from midealocal.devices.x26 import DeviceAttributes as X26Attributes
from midealocal.devices.x34 import DeviceAttributes as X34Attributes
from midealocal.devices.x40 import DeviceAttributes as X40Attributes

MIDEA_DEVICES: dict[int, dict[str, dict[str, Any] | str]] = {
    0x13: {
        "name": "Light",
        "entities": {
            "light": {"type": Platform.LIGHT, "icon": "mdi:lightbulb", "default": True},
        },
    },
    0x26: {
        "name": "Bathroom Master",
        "entities": {
            X26Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X26Attributes.current_humidity: {
                "type": Platform.SENSOR,
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X26Attributes.current_radar: {
                "type": Platform.BINARY_SENSOR,
                "name": "Occupancy Status",
                "device_class": BinarySensorDeviceClass.MOVING,
            },
            X26Attributes.main_light: {
                "type": Platform.SWITCH,
                "name": "Main Light",
                "icon": "mdi:lightbulb",
            },
            X26Attributes.night_light: {
                "type": Platform.SWITCH,
                "name": "Night Light",
                "icon": "mdi:lightbulb",
            },
            X26Attributes.mode: {
                "type": Platform.SELECT,
                "name": "Mode",
                "options": "preset_modes",
                "icon": "mdi:fan",
            },
            X26Attributes.direction: {
                "type": Platform.SELECT,
                "name": "Direction",
                "options": "directions",
                "icon": "mdi:arrow-split-vertical",
            },
        },
    },
    0x34: {
        "name": "Sink Dishwasher",
        "entities": {
            X34Attributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            X34Attributes.rinse_aid: {
                "type": Platform.BINARY_SENSOR,
                "name": "Rinse Aid Shortage",
                "icon": "mdi:bottle-tonic",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            X34Attributes.salt: {
                "type": Platform.BINARY_SENSOR,
                "name": "Salt Shortage",
                "icon": "mdi:drag",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            X34Attributes.humidity: {
                "type": Platform.SENSOR,
                "name": "Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X34Attributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            X34Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            X34Attributes.storage_remaining: {
                "type": Platform.SENSOR,
                "name": "Storage Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X34Attributes.temperature: {
                "type": Platform.SENSOR,
                "name": "Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X34Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X34Attributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            X34Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            X34Attributes.storage: {
                "type": Platform.SWITCH,
                "name": "Storage",
                "icon": "mdi:repeat-variant",
            },
            X34Attributes.mode: {
                "type": Platform.SENSOR,
                "name": "Working Mode",
                "icon": "mdi:dishwasher",
            },
            X34Attributes.error_code: {
                "type": Platform.SENSOR,
                "name": "Error Code",
                "icon": "mdi:alert-box",
            },
            X34Attributes.softwater: {
                "type": Platform.SENSOR,
                "name": "Softwater Level",
                "icon": "mdi:shaker-outline",
            },
            X34Attributes.bright: {
                "type": Platform.SENSOR,
                "name": "Bright Level",
                "icon": "mdi:star-four-points",
            },
        },
    },
    0x40: {
        "name": "Integrated Ceiling Fan",
        "entities": {
            "fan": {"type": Platform.FAN, "icon": "mdi:fan", "default": True},
            X40Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            X40Attributes.light: {
                "type": Platform.SWITCH,
                "name": "Light",
                "icon": "mdi:lightbulb",
            },
            X40Attributes.ventilation: {
                "type": Platform.SWITCH,
                "name": "Ventilation",
                "icon": "mdi:air-filter",
            },
            X40Attributes.smelly_sensor: {
                "type": Platform.SWITCH,
                "name": "Smelly Sensor",
                "icon": "mdi:scent",
            },
            X40Attributes.direction: {
                "type": Platform.SELECT,
                "name": "Direction",
                "options": "directions",
                "icon": "mdi:arrow-split-vertical",
            },
        },
    },
    0xA1: {
        "name": "Dehumidifier",
        "entities": {
            "humidifier": {
                "type": Platform.HUMIDIFIER,
                "icon": "mdi:air-humidifier",
                "default": True,
            },
            A1Attributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            A1Attributes.anion: {
                "type": Platform.SWITCH,
                "name": "Anion",
                "icon": "mdi:vanish",
            },
            A1Attributes.prompt_tone: {
                "type": Platform.SWITCH,
                "name": "Prompt Tone",
                "icon": "mdi:bell",
            },
            A1Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            A1Attributes.swing: {
                "type": Platform.SWITCH,
                "name": "swing",
                "icon": "mdi:pan-horizontal",
            },
            A1Attributes.fan_speed: {
                "type": Platform.SELECT,
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan",
            },
            A1Attributes.water_level_set: {
                "type": Platform.SELECT,
                "name": "Water Level Setting",
                "options": "water_level_sets",
                "icon": "mdi:cup-water",
            },
            A1Attributes.current_humidity: {
                "type": Platform.SENSOR,
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            A1Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            A1Attributes.tank: {
                "type": Platform.SENSOR,
                "name": "Tank",
                "icon": "mdi:cup-water",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            A1Attributes.tank_full: {
                "type": Platform.BINARY_SENSOR,
                "name": "Tank status",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
        },
    },
    0xAC: {
        "name": "Air Conditioner",
        "entities": {
            "climate": {
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "default": True,
            },
            "fresh_air": {"type": Platform.FAN, "icon": "mdi:fan", "name": "Fresh Air"},
            ACAttributes.aux_heating: {
                "type": Platform.SWITCH,
                "name": "Aux Heating",
                "icon": "mdi:heat-wave",
            },
            ACAttributes.boost_mode: {
                "type": Platform.SWITCH,
                "name": "Boost Mode",
                "icon": "mdi:turbine",
            },
            ACAttributes.breezeless: {
                "type": Platform.SWITCH,
                "name": "Breezeless",
                "icon": "mdi:tailwind",
            },
            ACAttributes.comfort_mode: {
                "type": Platform.SWITCH,
                "name": "Comfort Mode",
                "icon": "mdi:alpha-c-circle",
            },
            ACAttributes.dry: {
                "type": Platform.SWITCH,
                "name": "Dry",
                "icon": "mdi:air-filter",
            },
            ACAttributes.eco_mode: {
                "type": Platform.SWITCH,
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle",
            },
            ACAttributes.frost_protect: {
                "type": Platform.SWITCH,
                "name": "Frost Protect",
                "icon": "mdi:snowflake-alert",
            },
            ACAttributes.indirect_wind: {
                "type": Platform.SWITCH,
                "name": "Indirect Wind",
                "icon": "mdi:tailwind",
            },
            ACAttributes.natural_wind: {
                "type": Platform.SWITCH,
                "name": "Natural Wind",
                "icon": "mdi:tailwind",
            },
            ACAttributes.prompt_tone: {
                "type": Platform.SWITCH,
                "name": "Prompt Tone",
                "icon": "mdi:bell",
            },
            ACAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            ACAttributes.screen_display: {
                "type": Platform.SWITCH,
                "name": "Screen Display",
                "icon": "mdi:television-ambient-light",
            },
            ACAttributes.screen_display_alternate: {
                "type": Platform.SWITCH,
                "name": "Screen Display Alternate",
                "icon": "mdi:television-ambient-light",
            },
            ACAttributes.sleep_mode: {
                "type": Platform.SWITCH,
                "name": "Sleep Mode",
                "icon": "mdi:power-sleep",
            },
            ACAttributes.smart_eye: {
                "type": Platform.SWITCH,
                "name": "Smart Eye",
                "icon": "mdi:eye",
            },
            ACAttributes.swing_horizontal: {
                "type": Platform.SWITCH,
                "name": "Swing Horizontal",
                "icon": "mdi:arrow-split-vertical",
            },
            ACAttributes.swing_vertical: {
                "type": Platform.SWITCH,
                "name": "Swing Vertical",
                "icon": "mdi:arrow-split-horizontal",
            },
            ACAttributes.full_dust: {
                "type": Platform.BINARY_SENSOR,
                "name": "Full of Dust",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            ACAttributes.indoor_humidity: {
                "type": Platform.SENSOR,
                "name": "Indoor Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ACAttributes.indoor_temperature: {
                "type": Platform.SENSOR,
                "name": "Indoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ACAttributes.outdoor_temperature: {
                "type": Platform.SENSOR,
                "name": "Outdoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ACAttributes.total_energy_consumption: {
                "type": Platform.SENSOR,
                "name": "Total Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            ACAttributes.current_energy_consumption: {
                "type": Platform.SENSOR,
                "name": "Current Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            ACAttributes.realtime_power: {
                "type": Platform.SENSOR,
                "name": "Realtime Power",
                "device_class": SensorDeviceClass.POWER,
                "unit": UnitOfPower.WATT,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xB0: {
        "name": "Microwave Oven",
        "entities": {
            B0Attributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B0Attributes.tank_ejected: {
                "type": Platform.BINARY_SENSOR,
                "name": "Tank Ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B0Attributes.water_change_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B0Attributes.water_shortage: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B0Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B0Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            B0Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xB1: {
        "name": "Electric Oven",
        "entities": {
            B1Attributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B1Attributes.tank_ejected: {
                "type": Platform.BINARY_SENSOR,
                "name": "Tank ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B1Attributes.water_change_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B1Attributes.water_shortage: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B1Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B1Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            B1Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xB3: {
        "name": "Dish Sterilizer",
        "entities": {
            B3Attributes.top_compartment_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Top Compartment Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B3Attributes.top_compartment_preheating: {
                "type": Platform.BINARY_SENSOR,
                "name": "Top Compartment Preheating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.top_compartment_cooling: {
                "type": Platform.BINARY_SENSOR,
                "name": "Top Compartment Cooling",
                "icon": "snowflake-variant",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.middle_compartment_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Middle Compartment Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B3Attributes.middle_compartment_preheating: {
                "type": Platform.BINARY_SENSOR,
                "name": "Middle Compartment Preheating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.middle_compartment_cooling: {
                "type": Platform.BINARY_SENSOR,
                "name": "Middle Compartment Cooling",
                "icon": "snowflake-variant",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.bottom_compartment_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bottom Compartment Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B3Attributes.bottom_compartment_preheating: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bottom Compartment Preheating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.bottom_compartment_cooling: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bottom Compartment Cooling",
                "icon": "snowflake-variant",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            B3Attributes.top_compartment_status: {
                "type": Platform.SENSOR,
                "name": "Top Compartment Status",
                "icon": "mdi:information",
            },
            B3Attributes.top_compartment_temperature: {
                "type": Platform.SENSOR,
                "name": "Top Compartment Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B3Attributes.top_compartment_remaining: {
                "type": Platform.SENSOR,
                "name": "Top Compartment Remaining",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B3Attributes.middle_compartment_status: {
                "type": Platform.SENSOR,
                "name": "Middle Compartment Status",
                "icon": "mdi:information",
            },
            B3Attributes.middle_compartment_temperature: {
                "type": Platform.SENSOR,
                "name": "Middle Compartment Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B3Attributes.middle_compartment_remaining: {
                "type": Platform.SENSOR,
                "name": "Middle Compartment Remaining",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B3Attributes.bottom_compartment_status: {
                "type": Platform.SENSOR,
                "name": "Bottom Compartment Status",
                "icon": "mdi:information",
            },
            B3Attributes.bottom_compartment_temperature: {
                "type": Platform.SENSOR,
                "name": "Bottom Compartment Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B3Attributes.bottom_compartment_remaining: {
                "type": Platform.SENSOR,
                "name": "Bottom Compartment Remaining",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xB4: {
        "name": "Toaster",
        "entities": {
            B4Attributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            B4Attributes.tank_ejected: {
                "type": Platform.BINARY_SENSOR,
                "name": "Tank ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B4Attributes.water_change_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B4Attributes.water_shortage: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B4Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            B4Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            B4Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xB6: {
        "name": "Range Hood",
        "entities": {
            "fan": {"type": Platform.FAN, "icon": "mdi:fan", "default": True},
            B6Attributes.light: {
                "type": Platform.SWITCH,
                "name": "Light",
                "icon": "mdi:lightbulb",
            },
            B6Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            B6Attributes.cleaning_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Cleaning Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B6Attributes.oilcup_full: {
                "type": Platform.BINARY_SENSOR,
                "name": "Oil-cup Full",
                "icon": "mdi:cup",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            B6Attributes.fan_level: {
                "type": Platform.SENSOR,
                "name": "Fan level",
                "icon": "mdi:fan",
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xBF: {
        "name": "Microwave Steam Oven",
        "entities": {
            BFAttributes.tank_ejected: {
                "type": Platform.BINARY_SENSOR,
                "name": "Tank ejected",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            BFAttributes.water_change_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Change Reminder",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            BFAttributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            BFAttributes.water_shortage: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Shortage",
                "icon": "mdi:cup-water",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            BFAttributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            BFAttributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            BFAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xC2: {
        "name": "Toilet",
        "entities": {
            C2Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            C2Attributes.sensor_light: {
                "type": Platform.SWITCH,
                "name": "Sensor Light",
                "icon": "mdi:lightbulb",
            },
            C2Attributes.foam_shield: {
                "type": Platform.SWITCH,
                "name": "Foam Shield",
                "icon": "mdi:chart-bubble",
            },
            C2Attributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            C2Attributes.seat_status: {
                "type": Platform.BINARY_SENSOR,
                "name": "Seat Status",
                "icon": "mdi:seat-legroom-normal",
            },
            C2Attributes.lid_status: {
                "type": Platform.BINARY_SENSOR,
                "name": "Lid Status",
                "icon": "mdi:toilet",
            },
            C2Attributes.light_status: {
                "type": Platform.BINARY_SENSOR,
                "name": "Light Status",
                "icon": "mdi:lightbulb",
                "device_class": BinarySensorDeviceClass.LIGHT,
            },
            C2Attributes.water_temperature: {
                "type": Platform.SENSOR,
                "name": "Water Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            C2Attributes.seat_temperature: {
                "type": Platform.SENSOR,
                "name": "Seat Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            C2Attributes.filter_life: {
                "type": Platform.SENSOR,
                "name": "Filter Life",
                "icon": "mdi:toilet",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            C2Attributes.dry_level: {
                "type": Platform.NUMBER,
                "name": "Dry Level",
                "icon": "mdi:fire",
                "max": "max_dry_level",
                "min": 0,
                "step": 1,
            },
            C2Attributes.water_temp_level: {
                "type": Platform.NUMBER,
                "name": "Water Temperature Level",
                "icon": "mdi:fire",
                "max": "max_water_temp_level",
                "min": 0,
                "step": 1,
            },
            C2Attributes.seat_temp_level: {
                "type": Platform.NUMBER,
                "name": "Seat Temperature Level",
                "icon": "mdi:fire",
                "max": "max_seat_temp_level",
                "min": 0,
                "step": 1,
            },
        },
    },
    0xC3: {
        "name": "Heat Pump Wi-Fi Controller",
        "entities": {
            "climate_zone1": {
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "name": "Zone1 Thermostat",
                "zone": 0,
                "default": True,
            },
            "climate_zone2": {
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "name": "Zone2 Thermostat",
                "zone": 1,
                "default": False,
            },
            "water_heater": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:heat-pump",
                "name": "Domestic hot water",
                "default": True,
            },
            C3Attributes.disinfect: {
                "type": Platform.SWITCH,
                "name": "Disinfect",
                "icon": "mdi:water-plus-outline",
            },
            C3Attributes.dhw_power: {
                "type": Platform.SWITCH,
                "name": "DHW Power",
                "icon": "mdi:power",
            },
            C3Attributes.eco_mode: {
                "type": Platform.SWITCH,
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle",
            },
            C3Attributes.fast_dhw: {
                "type": Platform.SWITCH,
                "name": "Fast DHW",
                "icon": "mdi:rotate-orbit",
            },
            C3Attributes.silent_mode: {
                "type": Platform.SWITCH,
                "name": "Silent Mode",
                "icon": "mdi:fan-remove",
            },
            C3Attributes.tbh: {
                "type": Platform.SWITCH,
                "name": "TBH",
                "icon": "mdi:water-boiler",
            },
            C3Attributes.zone1_curve: {
                "type": Platform.SWITCH,
                "name": "Zone1 Curve",
                "icon": "mdi:chart-bell-curve-cumulative",
            },
            C3Attributes.zone2_curve: {
                "type": Platform.SWITCH,
                "name": "Zone2 Curve",
                "icon": "mdi:chart-bell-curve-cumulative",
            },
            C3Attributes.zone1_power: {
                "type": Platform.SWITCH,
                "name": "Zone1 Power",
                "icon": "mdi:power",
            },
            C3Attributes.zone2_power: {
                "type": Platform.SWITCH,
                "name": "Zone2 Power",
                "icon": "mdi:power",
            },
            C3Attributes.zone1_water_temp_mode: {
                "type": Platform.BINARY_SENSOR,
                "name": "Zone1 Water-temperature Mode",
                "icon": "mdi:coolant-temperature",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone2_water_temp_mode: {
                "type": Platform.BINARY_SENSOR,
                "name": "Zone2 Water-temperature Mode",
                "icon": "mdi:coolant-temperature",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone1_room_temp_mode: {
                "type": Platform.BINARY_SENSOR,
                "name": "Zone1 Room-temperature Mode",
                "icon": "mdi:home-thermometer-outline",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.zone2_room_temp_mode: {
                "type": Platform.BINARY_SENSOR,
                "name": "Zone2 Room-temperature Mode",
                "icon": "mdi:home-thermometer-outline",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.error_code: {
                "type": Platform.SENSOR,
                "name": "Error Code",
                "icon": "mdi:alpha-e-circle",
            },
            C3Attributes.tank_actual_temperature: {
                "type": Platform.SENSOR,
                "name": "Tank Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            C3Attributes.status_dhw: {
                "type": Platform.BINARY_SENSOR,
                "name": "DHW status",
                "icon": "mdi:heat-pump",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.status_tbh: {
                "type": Platform.BINARY_SENSOR,
                "name": "TBH status",
                "icon": "mdi:water-boiler",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.status_ibh: {
                "type": Platform.BINARY_SENSOR,
                "name": "IBH status",
                "icon": "mdi:coolant-temperature",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.status_heating: {
                "type": Platform.BINARY_SENSOR,
                "name": "Heating status",
                "icon": "mdi:heat-pump",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            C3Attributes.total_energy_consumption: {
                "type": Platform.SENSOR,
                "name": "Total energy consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            C3Attributes.total_produced_energy: {
                "type": Platform.SENSOR,
                "name": "Total produced energy",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            C3Attributes.outdoor_temperature: {
                "type": Platform.SENSOR,
                "name": "Outdoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xCA: {
        "name": "Refrigerator",
        "entities": {
            CAAttributes.bar_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bar Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            CAAttributes.bar_door_overtime: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bar Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CAAttributes.flex_zone_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Flex Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            CAAttributes.flex_zone_door_overtime: {
                "type": Platform.BINARY_SENSOR,
                "name": "Flex Zone Door",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CAAttributes.freezer_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Freezer Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            CAAttributes.freezer_door_overtime: {
                "type": Platform.BINARY_SENSOR,
                "name": "Freezer Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CAAttributes.refrigerator_door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Refrigerator Door",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CAAttributes.refrigerator_door_overtime: {
                "type": Platform.BINARY_SENSOR,
                "name": "Refrigerator Door Overtime",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CAAttributes.flex_zone_actual_temp: {
                "type": Platform.SENSOR,
                "name": "Flex Zone Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.flex_zone_setting_temp: {
                "type": Platform.SENSOR,
                "name": "Flex Zone Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.freezer_actual_temp: {
                "type": Platform.SENSOR,
                "name": "Freezer Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.freezer_setting_temp: {
                "type": Platform.SENSOR,
                "name": "Freezer Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.energy_consumption: {
                "type": Platform.SENSOR,
                "name": "Energy Consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "unit": UnitOfEnergy.KILO_WATT_HOUR,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            CAAttributes.refrigerator_actual_temp: {
                "type": Platform.SENSOR,
                "name": "Refrigerator Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.refrigerator_setting_temp: {
                "type": Platform.SENSOR,
                "name": "Refrigerator Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.right_flex_zone_actual_temp: {
                "type": Platform.SENSOR,
                "name": "Right Flex Zone Actual Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CAAttributes.right_flex_zone_setting_temp: {
                "type": Platform.SENSOR,
                "name": "Right Flex Zone Setting Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xCC: {
        "name": "MDV Wi-Fi Controller",
        "entities": {
            "climate": {
                "type": Platform.CLIMATE,
                "icon": "hass:air-conditioner",
                "default": True,
            },
            CCAttributes.aux_heating: {
                "type": Platform.SWITCH,
                "name": "Aux Heating",
                "icon": "mdi:heat-wave",
            },
            CCAttributes.eco_mode: {
                "type": Platform.SWITCH,
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle",
            },
            CCAttributes.night_light: {
                "type": Platform.SWITCH,
                "name": "Night Light",
                "icon": "mdi:lightbulb",
            },
            CCAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            CCAttributes.sleep_mode: {
                "type": Platform.SWITCH,
                "name": "Sleep Mode",
                "icon": "mdi:power-sleep",
            },
            CCAttributes.swing: {
                "type": Platform.SWITCH,
                "name": "Swing",
                "icon": "mdi:arrow-split-horizontal",
            },
            CCAttributes.indoor_temperature: {
                "type": Platform.SENSOR,
                "name": "Indoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xCD: {
        "name": "Heat Pump Water Heater",
        "entities": {
            "water_heater": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:heat-pump",
                "default": True,
            },
            CDAttributes.compressor_status: {
                "type": Platform.BINARY_SENSOR,
                "name": "Compressor Status",
                "icon": "mdi:drag",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            CDAttributes.compressor_temperature: {
                "type": Platform.SENSOR,
                "name": "Compressor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CDAttributes.condenser_temperature: {
                "type": Platform.SENSOR,
                "name": "Condenser Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CDAttributes.outdoor_temperature: {
                "type": Platform.SENSOR,
                "name": "Outdoor Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CDAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
        },
    },
    0xCE: {
        "name": "Fresh Air Appliance",
        "entities": {
            "fan": {"type": Platform.FAN, "icon": "mdi:fan", "default": True},
            CEAttributes.filter_cleaning_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Filter Cleaning Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CEAttributes.filter_change_reminder: {
                "type": Platform.BINARY_SENSOR,
                "name": "Filter Change Reminder",
                "icon": "mdi:alert-circle",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            CEAttributes.current_humidity: {
                "type": Platform.SENSOR,
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CEAttributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CEAttributes.co2: {
                "type": Platform.SENSOR,
                "name": "Carbon Dioxide",
                "device_class": SensorDeviceClass.CO2,
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CEAttributes.hcho: {
                "type": Platform.SENSOR,
                "name": "Methanal",
                "icon": "mdi:molecule",
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CEAttributes.pm25: {
                "type": Platform.SENSOR,
                "name": "PM 2.5",
                "device_class": SensorDeviceClass.PM25,
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            CEAttributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            CEAttributes.aux_heating: {
                "type": Platform.SWITCH,
                "name": "Aux Heating",
                "icon": "mdi:heat-wave",
            },
            CEAttributes.eco_mode: {
                "type": Platform.SWITCH,
                "name": "ECO Mode",
                "icon": "mdi:leaf-circle",
            },
            CEAttributes.link_to_ac: {
                "type": Platform.SWITCH,
                "name": "Link to AC",
                "icon": "mdi:link",
            },
            CEAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            CEAttributes.powerful_purify: {
                "type": Platform.SWITCH,
                "name": "Powerful Purification",
                "icon": "mdi:turbine",
            },
            CEAttributes.sleep_mode: {
                "type": Platform.SWITCH,
                "name": "Sleep Mode",
                "icon": "mdi:power-sleep",
            },
        },
    },
    0xCF: {
        "name": "Heat Pump",
        "entities": {
            "climate": {
                "type": Platform.CLIMATE,
                "icon": "hass:air-conditioner",
                "default": True,
            },
            CFAttributes.aux_heating: {
                "type": Platform.SWITCH,
                "name": "Aux Heating",
                "icon": "mdi:heat-wave",
            },
            CFAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            CFAttributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xDA: {
        "name": "Top Load Washer",
        "entities": {
            DAAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DAAttributes.wash_time: {
                "type": Platform.SENSOR,
                "name": "wash time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DAAttributes.soak_time: {
                "type": Platform.SENSOR,
                "name": "soak time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DAAttributes.dehydration_time: {
                "type": Platform.SENSOR,
                "name": "dehydration time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DAAttributes.dehydration_speed: {
                "type": Platform.SENSOR,
                "name": "dehydration speed",
                "icon": "mdi:speedometer",
            },
            DAAttributes.error_code: {
                "type": Platform.SENSOR,
                "name": "error code",
                "icon": "mdi:washing-machine-alert",
            },
            DAAttributes.rinse_count: {
                "type": Platform.SENSOR,
                "name": "rinse count",
                "icon": "mdi:water-sync",
            },
            DAAttributes.rinse_level: {
                "type": Platform.SENSOR,
                "name": "rinse level",
                "icon": "mdi:hydraulic-oil-level",
            },
            DAAttributes.wash_level: {
                "type": Platform.SENSOR,
                "name": "rinse count",
                "icon": "mdi:hydraulic-oil-level",
            },
            DAAttributes.wash_strength: {
                "type": Platform.SENSOR,
                "name": "wash strength",
                "icon": "mdi:network-strength-4-cog",
            },
            DAAttributes.softener: {
                "type": Platform.SENSOR,
                "name": "softener",
                "icon": "mdi:tshirt-crew",
            },
            DAAttributes.detergent: {
                "type": Platform.SENSOR,
                "name": "detergent",
                "icon": "mdi:spray-bottle",
            },
            DAAttributes.program: {
                "type": Platform.SENSOR,
                "name": "Program",
                "icon": "mdi:progress-wrench",
            },
            DAAttributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            DAAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            DAAttributes.start: {
                "type": Platform.SWITCH,
                "name": "Start",
                "icon": "mdi:motion-play-outline",
            },
        },
    },
    0xDB: {
        "name": "Front Load Washer",
        "entities": {
            DBAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DBAttributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            DBAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            DBAttributes.start: {
                "type": Platform.SWITCH,
                "name": "Start",
                "icon": "mdi:motion-play-outline",
            },
        },
    },
    0xDC: {
        "name": "Clothes Dryer",
        "entities": {
            DCAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DCAttributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            DCAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            DCAttributes.start: {
                "type": Platform.SWITCH,
                "name": "Start",
                "icon": "mdi:motion-play-outline",
            },
        },
    },
    0xE1: {
        "name": "Dishwasher",
        "entities": {
            E1Attributes.door: {
                "type": Platform.BINARY_SENSOR,
                "name": "Door",
                "icon": "mdi:box-shadow",
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            E1Attributes.rinse_aid: {
                "type": Platform.BINARY_SENSOR,
                "name": "Rinse Aid Shortage",
                "icon": "mdi:bottle-tonic",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            E1Attributes.salt: {
                "type": Platform.BINARY_SENSOR,
                "name": "Salt Shortage",
                "icon": "mdi:drag",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            E1Attributes.humidity: {
                "type": Platform.SENSOR,
                "name": "Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E1Attributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            E1Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            E1Attributes.storage_remaining: {
                "type": Platform.SENSOR,
                "name": "Storage Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.HOURS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E1Attributes.temperature: {
                "type": Platform.SENSOR,
                "name": "Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E1Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E1Attributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            E1Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            E1Attributes.storage: {
                "type": Platform.SWITCH,
                "name": "Storage",
                "icon": "mdi:repeat-variant",
            },
            E1Attributes.mode: {
                "type": Platform.SENSOR,
                "name": "Working Mode",
                "icon": "mdi:dishwasher",
            },
            E1Attributes.error_code: {
                "type": Platform.SENSOR,
                "name": "Error Code",
                "icon": "mdi:alert-box",
            },
            E1Attributes.softwater: {
                "type": Platform.SENSOR,
                "name": "Softwater Level",
                "icon": "mdi:shaker-outline",
            },
            E1Attributes.bright: {
                "type": Platform.SENSOR,
                "name": "Bright Level",
                "icon": "mdi:star-four-points",
            },
        },
    },
    0xE2: {
        "name": "Electric Water Heater",
        "entities": {
            "water_heater": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:meter-electric-outline",
                "default": True,
            },
            E2Attributes.heating: {
                "type": Platform.BINARY_SENSOR,
                "name": "Heating",
                "icon": "mdi:heat-wave",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E2Attributes.keep_warm: {
                "type": Platform.BINARY_SENSOR,
                "name": "Keep Warm",
                "icon": "mdi:menu",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E2Attributes.protection: {
                "type": Platform.BINARY_SENSOR,
                "name": "Protection",
                "icon": "mdi:shield-check",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E2Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E2Attributes.heating_time_remaining: {
                "type": Platform.SENSOR,
                "name": "Heating Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E2Attributes.heating_power: {
                "type": Platform.SENSOR,
                "name": "Heating Power",
                "device_class": SensorDeviceClass.POWER,
                "unit": UnitOfPower.WATT,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E2Attributes.water_consumption: {
                "type": Platform.SENSOR,
                "name": "Water Consumption",
                "icon": "mdi:water",
                "unit": UnitOfVolume.LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
            E2Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            E2Attributes.variable_heating: {
                "type": Platform.SWITCH,
                "name": "Variable Heating",
                "icon": "mdi:waves",
            },
            E2Attributes.whole_tank_heating: {
                "type": Platform.SWITCH,
                "name": "Whole Tank Heating",
                "icon": "mdi:restore",
            },
        },
    },
    0xE3: {
        "name": "Gas Water Heater",
        "entities": {
            "water_heater": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:meter-gas",
                "default": True,
            },
            E3Attributes.burning_state: {
                "type": Platform.BINARY_SENSOR,
                "name": "Burning State",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E3Attributes.protection: {
                "type": Platform.BINARY_SENSOR,
                "name": "Protection",
                "icon": "mdi:shield-check",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E3Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E3Attributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            E3Attributes.smart_volume: {
                "type": Platform.SWITCH,
                "name": "Smart Volume",
                "icon": "mdi:recycle",
            },
            E3Attributes.zero_cold_water: {
                "type": Platform.SWITCH,
                "name": "Zero Cold Water",
                "icon": "mdi:restore",
            },
            E3Attributes.zero_cold_pulse: {
                "type": Platform.SWITCH,
                "name": "Zero Cold Water (Pulse)",
                "icon": "mdi:restore-alert",
            },
        },
    },
    0xE6: {
        "name": "Gas Boilers",
        "entities": {
            "water_heater_heating": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:meter-gas",
                "name": "Heating",
                "use": 0,
                "default": True,
            },
            "water_heater_bathing": {
                "type": Platform.WATER_HEATER,
                "icon": "mdi:meter-gas",
                "name": "Bathing",
                "use": 1,
                "default": True,
            },
            E6Attributes.heating_working: {
                "type": Platform.BINARY_SENSOR,
                "name": "Heating Working Status",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E6Attributes.bathing_working: {
                "type": Platform.BINARY_SENSOR,
                "name": "Bathing Working Status",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            E6Attributes.heating_leaving_temperature: {
                "type": Platform.SENSOR,
                "name": "Heating Leaving Water Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E6Attributes.bathing_leaving_temperature: {
                "type": Platform.SENSOR,
                "name": "Bathing Leaving Water Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E6Attributes.main_power: {
                "type": Platform.SWITCH,
                "name": "Main Power",
                "icon": "mdi:power",
            },
            E6Attributes.heating_power: {
                "type": Platform.SWITCH,
                "name": "Heating Power",
                "icon": "mdi:heating-coil",
            },
        },
    },
    0xE8: {
        "name": "Electric Slow Cooker",
        "entities": {
            E8Attributes.finished: {
                "type": Platform.BINARY_SENSOR,
                "name": "Finished",
                "icon": "",
            },
            E8Attributes.water_shortage: {
                "type": Platform.BINARY_SENSOR,
                "name": "Water Shortage",
                "icon": "mdi:drag",
                "device_class": BinarySensorDeviceClass.PROBLEM,
            },
            E8Attributes.status: {
                "type": Platform.SENSOR,
                "name": "Status",
                "icon": "mdi:information",
            },
            E8Attributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E8Attributes.keep_warm_remaining: {
                "type": Platform.SENSOR,
                "name": "Keep Warm Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E8Attributes.working_time: {
                "type": Platform.SENSOR,
                "name": "Working Time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.SECONDS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E8Attributes.target_temperature: {
                "type": Platform.SENSOR,
                "name": "Target Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            E8Attributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xEA: {
        "name": "Electric Rice Cooker",
        "entities": {
            EAAttributes.cooking: {
                "type": Platform.BINARY_SENSOR,
                "name": "Cooking",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            EAAttributes.keep_warm: {
                "type": Platform.BINARY_SENSOR,
                "name": "Keep Warm",
                "icon": "mdi:menu",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            EAAttributes.bottom_temperature: {
                "type": Platform.SENSOR,
                "name": "Bottom Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EAAttributes.keep_warm_time: {
                "type": Platform.SENSOR,
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EAAttributes.mode: {
                "type": Platform.SENSOR,
                "name": "Mode",
                "icon": "mdi:orbit",
            },
            EAAttributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            EAAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EAAttributes.top_temperature: {
                "type": Platform.SENSOR,
                "name": "Top Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xEC: {
        "name": "Electric Pressure Cooker",
        "entities": {
            ECAttributes.cooking: {
                "type": Platform.BINARY_SENSOR,
                "name": "Cooking",
                "icon": "mdi:fire",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            ECAttributes.with_pressure: {
                "type": Platform.BINARY_SENSOR,
                "name": "With Pressure",
                "icon": "mdi:information",
                "device_class": BinarySensorDeviceClass.RUNNING,
            },
            ECAttributes.bottom_temperature: {
                "type": Platform.SENSOR,
                "name": "Bottom Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ECAttributes.keep_warm_time: {
                "type": Platform.SENSOR,
                "name": "Keep Warm Time",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ECAttributes.mode: {
                "type": Platform.SENSOR,
                "name": "Mode",
                "icon": "mdi:orbit",
            },
            ECAttributes.progress: {
                "type": Platform.SENSOR,
                "name": "Progress",
                "icon": "mdi:rotate-360",
            },
            ECAttributes.time_remaining: {
                "type": Platform.SENSOR,
                "name": "Time Remaining",
                "icon": "mdi:progress-clock",
                "unit": UnitOfTime.MINUTES,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            ECAttributes.top_temperature: {
                "type": Platform.SENSOR,
                "name": "Top Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xED: {
        "name": "Water Drinking Appliance",
        "entities": {
            EDAttributes.child_lock: {
                "type": Platform.LOCK,
                "has_entity_name": True,
                "translation_key": "child_lock",
                "name": "Child Lock",
            },
            EDAttributes.power: {
                "type": Platform.SWITCH,
                "has_entity_name": True,
                "translation_key": "power",
                "name": "Power",
                "icon": "mdi:power",
            },
            EDAttributes.filter1: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter1_days",
                "name": "Filter1 Available Days",
                "icon": "mdi:air-filter",
                "unit": UnitOfTime.DAYS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.filter2: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter2_days",
                "name": "Filter2 Available Days",
                "icon": "mdi:air-filter",
                "unit": UnitOfTime.DAYS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.filter3: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter3_days",
                "name": "Filter3 Available Days",
                "icon": "mdi:air-filter",
                "unit": UnitOfTime.DAYS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.life1: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter1_life",
                "name": "Filter1 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.life2: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter2_life",
                "name": "Filter2 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.life3: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "filter3_life",
                "name": "Filter3 Life Level",
                "icon": "mdi:percent",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.in_tds: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "in_tds",
                "name": "In TDS",
                "icon": "mdi:water",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.out_tds: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "out_tds",
                "name": "Out TDS",
                "icon": "mdi:water-plus",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            EDAttributes.water_consumption: {
                "type": Platform.SENSOR,
                "has_entity_name": True,
                "translation_key": "water_consumption",
                "name": "Water Consumption",
                "icon": "mdi:water-pump",
                "unit": UnitOfVolume.LITERS,
                "state_class": SensorStateClass.TOTAL_INCREASING,
            },
        },
    },
    0xFA: {
        "name": "Fan",
        "entities": {
            "fan": {"type": Platform.FAN, "icon": "mdi:fan", "default": True},
            FAAttributes.oscillation_mode: {
                "type": Platform.SELECT,
                "name": "Oscillation Mode",
                "options": "oscillation_modes",
                "icon": "mdi:swap-horizontal-variant",
            },
            FAAttributes.oscillation_angle: {
                "type": Platform.SELECT,
                "name": "Oscillation Angle",
                "options": "oscillation_angles",
                "icon": "mdi:pan-horizontal",
            },
            FAAttributes.tilting_angle: {
                "type": Platform.SELECT,
                "name": "Tilting Angle",
                "options": "tilting_angles",
                "icon": "mdi:pan-vertical",
            },
            FAAttributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            FAAttributes.oscillate: {
                "type": Platform.SWITCH,
                "name": "Oscillate",
                "icon": "mdi:swap-horizontal-bold",
            },
            FAAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
        },
    },
    0xFB: {
        "name": "Electric Heater",
        "entities": {
            "climate": {
                "type": Platform.CLIMATE,
                "icon": "mdi:air-conditioner",
                "default": True,
            },
            FBAttributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            FBAttributes.heating_level: {
                "type": Platform.NUMBER,
                "name": "Heating Level",
                "icon": "mdi:fire",
                "max": 10,
                "min": 1,
                "step": 1,
            },
            FBAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            FBAttributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xFC: {
        "name": "Air Purifier",
        "entities": {
            FCAttributes.child_lock: {"type": Platform.LOCK, "name": "Child Lock"},
            FCAttributes.anion: {
                "type": Platform.SWITCH,
                "name": "Anion",
                "icon": "mdi:vanish",
            },
            FCAttributes.prompt_tone: {
                "type": Platform.SWITCH,
                "name": "Prompt Tone",
                "icon": "mdi:bell",
            },
            FCAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            FCAttributes.standby: {
                "type": Platform.SWITCH,
                "name": "Standby",
                "icon": "mdi:smoke-detector-variant",
            },
            FCAttributes.detect_mode: {
                "type": Platform.SELECT,
                "name": "Detect Mode",
                "options": "detect_modes",
                "icon": "mdi:smoke-detector-variant",
            },
            FCAttributes.mode: {
                "type": Platform.SELECT,
                "name": "Mode",
                "options": "modes",
                "icon": "mdi:rotate-360",
            },
            FCAttributes.fan_speed: {
                "type": Platform.SELECT,
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan",
            },
            FCAttributes.screen_display: {
                "type": Platform.SELECT,
                "name": "Screen Display",
                "options": "screen_displays",
                "icon": "mdi:television-ambient-light",
            },
            FCAttributes.pm25: {
                "type": Platform.SENSOR,
                "name": "PM 2.5",
                "device_class": SensorDeviceClass.PM25,
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            FCAttributes.tvoc: {
                "type": Platform.SENSOR,
                "name": "TVOC",
                "icon": "mdi:heat-wave",
                "unit": CONCENTRATION_PARTS_PER_MILLION,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            FCAttributes.hcho: {
                "type": Platform.SENSOR,
                "name": "Methanal",
                "icon": "mdi:molecule",
                "unit": CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            FCAttributes.filter1_life: {
                "type": Platform.SENSOR,
                "name": "Filter1 Life Level",
                "icon": "mdi:air-filter",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            FCAttributes.filter2_life: {
                "type": Platform.SENSOR,
                "name": "Filter2 Life Level",
                "icon": "mdi:air-filter",
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
    0xFD: {
        "name": "Humidifier",
        "entities": {
            Platform.HUMIDIFIER: {
                "type": Platform.HUMIDIFIER,
                "icon": "mdi:air-humidifier",
                "default": True,
            },
            FDAttributes.disinfect: {
                "type": Platform.SWITCH,
                "name": "Disinfect",
                "icon": "mdi:water-plus-outline",
            },
            FDAttributes.prompt_tone: {
                "type": Platform.SWITCH,
                "name": "Prompt Tone",
                "icon": "mdi:bell",
            },
            FDAttributes.power: {
                "type": Platform.SWITCH,
                "name": "Power",
                "icon": "mdi:power",
            },
            FDAttributes.fan_speed: {
                "type": Platform.SELECT,
                "name": "Fan Speed",
                "options": "fan_speeds",
                "icon": "mdi:fan",
            },
            FDAttributes.screen_display: {
                "type": Platform.SELECT,
                "name": "Screen Display",
                "options": "screen_displays",
                "icon": "mdi:television-ambient-light",
            },
            FDAttributes.current_humidity: {
                "type": Platform.SENSOR,
                "name": "Current Humidity",
                "device_class": SensorDeviceClass.HUMIDITY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            FDAttributes.current_temperature: {
                "type": Platform.SENSOR,
                "name": "Current Temperature",
                "device_class": SensorDeviceClass.TEMPERATURE,
                "unit": UnitOfTemperature.CELSIUS,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        },
    },
}
