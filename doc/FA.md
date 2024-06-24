# Fan

## Features

- Supports fan speed
- Supports preset mode
- Supports oscillation
- Supports tilting

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

| EntityID                             | Class  | Description       |
| ------------------------------------ | ------ | ----------------- |
| select.{DEVICEID}\_oscillation_mode  | select | Oscillation Mode  |
| select.{DEVICEID}\_oscillation_angle | select | Oscillation Angle |
| select.{DEVICEID}\_tilting_angle     | select | Tilting Angle     |
| lock.{DEVICEID}\_child_lock          | lock   | Child Lock        |
| switch.{DEVICEID}\_oscillate         | switch | Oscillate         |
| switch.{DEVICEID}\_power             | switch | Power             |

## Services

### midea_lan.set_attribute

[![Service](https://my.home-assistant.io/badges/developer_call_service.svg)](https://my.home-assistant.io/redirect/developer_call_service/?service=midea_lan.set_attribute)

Set the attribute of appliance. Service data:

| Name      | Description                                 |
| --------- | ------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance |
| attribute | "child_lock"<br/>"oscillate"                |
| value     | true or false                               |

| Name      | Description                                                                                 |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                 |
| attribute | "oscillation_mode"                                                                          |
| value     | "Off"<br/>"Oscillation"<br/>"Tilting"<br/>"Curve-W"<br/>"Curve-8"<br/>"Reserved"<br/>"Both" |

| Name      | Description                                                    |
| --------- | -------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                    |
| attribute | "oscillation_angle"                                            |
| value     | "Off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360" |

| Name      | Description                                                                                 |
| --------- | ------------------------------------------------------------------------------------------- |
| device_id | The Appliance code (Device ID) of appliance                                                 |
| attribute | "tilting_angle"                                                                             |
| value     | "Off"<br/>"30"<br/>"60"<br/>"90"<br/>"120"<br/>"180"<br/>"360"<br/>"+60"<br/>"-60"<br/>"40" |

Example

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: power
  value: true
```

```yaml
service: midea_lan.set_attribute
data:
  device_id: XXXXXXXXXXXX
  attribute: oscillation_angle
  value: "90"
```
