# Humidifier

## Features

- Supports preset mode
- Supports fan mode
- Supports humidity setting

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
| select.{DEVICEID}\_fan_speed           | select | Fan Speed           |
| select.{DEVICEID}\_screen_display      | select | Screen Display      |

## Service

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "disinfect"<br/>"prompt_tone"<br/>"power"   |
| value     | true or false                               |

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

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: prompt_tone
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: fan_speed
  value: Medium
```
