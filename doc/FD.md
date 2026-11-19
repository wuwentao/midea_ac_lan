# Humidifier

## Features

- Supports preset mode
- Supports fan mode
- Supports humidity setting
- Supports protocol-specific mode, fan, and display layouts
- Supports wet-pad drying on Lua `2024110101` devices

## Entities

### Default entity

| EntityID                          | Class      | Description       |
| --------------------------------- | ---------- | ----------------- |
| humidifier.{DEVICEID}\_humidifier | humidifier | Humidifier entity |

### Extra entities

| EntityID                               | Class  | Description         |
| -------------------------------------- | ------ | ------------------- |
| sensor.{DEVICEID}\_current_humidity    | sensor | Current Humidity    |
| sensor.{DEVICEID}\_current_temperature | sensor | Current Temperature |
| switch.{DEVICEID}\_disinfect           | switch | Disinfect           |
| switch.{DEVICEID}\_prompt_tone         | switch | Prompt Tone         |
| switch.{DEVICEID}\_power               | switch | Power               |
| switch.{DEVICEID}\_wet_pad_dry         | switch | Wet Pad Drying      |
| select.{DEVICEID}\_fan_speed           | select | Fan Speed           |
| select.{DEVICEID}\_screen_display      | select | Screen Display      |

## Service

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                 |
| --------- | ----------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                 |
| attribute | "disinfect"<br/>"prompt_tone"<br/>"power"<br/>"wet_pad_dry" |
| value     | true or false                                               |

| Name      | Description                                                     |
| --------- | --------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                     |
| attribute | "fan_speed"                                                     |
| value     | "Lowest"<br/>"Low"<br/>"Medium"<br/>"High"<br/>"Auto"<br/>"Off" |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "screen_display"                            |
| value     | "Bright"<br/>"Dim"<br/>"Off"                |

Available modes, fan speeds, and screen display choices depend on the
automatically detected device protocol. Lua 25 devices expose their verified
fan choices without `Off`; their display choices are `Bright`/`Off`, without
`Dim`. Lua `2024110101` devices expose `Manual`/`Sleep`/`Moist skin`,
`Low`/`Medium`/`High`, and `Bright`/`Dim`/`Off`.

Wet-pad drying is an optional extra switch. It is offered in the integration
options only after a Lua `2024110101` status message reports the capability.

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: prompt_tone
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: Medium
```
