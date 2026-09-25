# Fan

## Features

- Supports fan speed
- Supports preset mode
- Supports oscillation
- Supports tilting
- Supports humidification, water ions, anion and anti-mosquito
- Supports display, auto power off and body-feeling scan
- Reports humidity, target temperature and error code

## Customize

Set the levels of the fan device except "Off" (3 by default).

```json
{ "speed_count": 5 }
```

## Entities

### Default entity

| EntityID            | Class | Description |
| ------------------- | ----- | ----------- |
| fan.{DEVICEID}\_fan | fan   | Fan entity  |

### Extra entities

| EntityID                                | Class  | Description          |
| --------------------------------------- | ------ | -------------------- |
| select.{DEVICEID}\_oscillation_mode     | select | Oscillation Mode     |
| select.{DEVICEID}\_oscillation_angle    | select | Oscillation Angle    |
| select.{DEVICEID}\_tilting_angle        | select | Tilting Angle        |
| lock.{DEVICEID}\_child_lock             | lock   | Child Lock           |
| switch.{DEVICEID}\_oscillate            | switch | Oscillate            |
| switch.{DEVICEID}\_power                | switch | Power                |
| switch.{DEVICEID}\_humidify             | switch | Humidify             |
| switch.{DEVICEID}\_waterions            | switch | Water Ions           |
| switch.{DEVICEID}\_anion                | switch | Anion                |
| switch.{DEVICEID}\_anophelifuge         | switch | Anti-Mosquito        |
| switch.{DEVICEID}\_display_on_off       | switch | Display              |
| switch.{DEVICEID}\_auto_power_off       | switch | Auto Power Off       |
| switch.{DEVICEID}\_body_feeling_scan    | switch | Body Feeling Scan    |
| sensor.{DEVICEID}\_humidity             | sensor | Humidity             |
| sensor.{DEVICEID}\_target_temperature   | sensor | Target Temperature   |
| sensor.{DEVICEID}\_humidify_feedback    | sensor | Humidity Feedback    |
| sensor.{DEVICEID}\_temperature_feedback | sensor | Temperature Feedback |
| sensor.{DEVICEID}\_humidify_mode        | sensor | Humidify Mode        |
| sensor.{DEVICEID}\_error_code           | sensor | Error Code           |

## Services

### midea_ac_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_ac_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                                                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| device_id | The Appliance code (Device ID) of appliance                                                                                                                  |
| attribute | "child_lock"<br/>"oscillate"<br/>"humidify"<br/>"waterions"<br/>"anion"<br/>"anophelifuge"<br/>"display_on_off"<br/>"auto_power_off"<br/>"body_feeling_scan" |
| value     | true or false                                                                                                                                                |

| Name      | Description                                                                                              |
| --------- | -------------------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                              |
| attribute | "oscillation_mode"                                                                                       |
| value     | "off"<br/>"oscillation"<br/>"tilting"<br/>"curve_w"<br/>"curve_8"<br/>"reserved"<br/>"both"<br/>"custom" |

| Name      | Description                                                    |
| --------- | -------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                    |
| attribute | "oscillation_angle"                                            |
| value     | "off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360" |

| Name      | Description                                                                                 |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                 |
| attribute | "tilting_angle"                                                                             |
| value     | "off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360"<br/>"+60"<br/>"-60"<br/>"40" |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "target_temperature"                        |
| value     | Target temperature in °C                    |

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "humidity"                                  |
| value     | Target humidity in % (1-100)                |

Example

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_ac_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: oscillation_angle
  value: "90"
```
